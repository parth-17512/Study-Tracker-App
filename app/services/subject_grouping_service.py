import re
import json
import logging
from typing import Dict, List, Any, Optional
from app.ai.providers.router import FallbackProviderRouter

logger = logging.getLogger(__name__)

class SubjectGroupingService:
    """
    Groups similar study subjects/topics into broader learning areas.
    Uses LLM for semantic categorization and deterministic Python code for totals.
    Guarantees non-destructive operation: original records are never altered.
    """

    def __init__(self, provider_router: Optional[FallbackProviderRouter] = None):
        self.router = provider_router or FallbackProviderRouter()

    def group_topics(self, topic_distribution: Dict[str, int]) -> Dict[str, Any]:
        """
        Groups topic names into broader learning areas and deterministically computes totals.

        Args:
            topic_distribution: Dict[topic_name, total_duration_seconds]

        Returns:
            Dict containing:
                'total_seconds': int
                'groups': List of dicts, each with:
                    'label': str (e.g. 'Python')
                    'total_seconds': int
                    'formatted_duration': str
                    'percentage': float
                    'topics': List of original topic dicts [{'name': ..., 'seconds': ..., 'formatted': ...}]
        """
        if not topic_distribution:
            return {
                "total_seconds": 0,
                "groups": []
            }

        total_seconds = sum(topic_distribution.values())
        topics = list(topic_distribution.keys())

        # If only 1 topic, no grouping needed
        if len(topics) == 1:
            sec = topic_distribution[topics[0]]
            h = sec // 3600
            m = (sec % 3600) // 60
            dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"
            return {
                "total_seconds": total_seconds,
                "groups": [{
                    "label": topics[0],
                    "total_seconds": sec,
                    "total_minutes": sec // 60,
                    "formatted_duration": dur_str,
                    "percentage": 100.0,
                    "topics": [{
                        "name": topics[0],
                        "seconds": sec,
                        "formatted": dur_str
                    }]
                }]
            }

        # Attempt LLM Semantic Grouping
        group_mapping = self._get_semantic_grouping_from_llm(topics)

        # If LLM grouping was incomplete or failed, fallback to conservative rule-based grouping
        if not group_mapping:
            group_mapping = self._conservative_rule_grouping(topics)

        # Deterministic Aggregation (Application Code calculation)
        groups = []
        covered_topics = set()

        for group_label, member_topics in group_mapping.items():
            valid_members = [t for t in member_topics if t in topic_distribution]
            if not valid_members:
                continue

            group_sec = sum(topic_distribution[t] for t in valid_members)
            h = group_sec // 3600
            m = (group_sec % 3600) // 60
            dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"
            pct = (group_sec / total_seconds * 100) if total_seconds > 0 else 0.0

            member_details = []
            for t in valid_members:
                covered_topics.add(t)
                t_sec = topic_distribution[t]
                th = t_sec // 3600
                tm = (t_sec % 3600) // 60
                member_details.append({
                    "name": t,
                    "seconds": t_sec,
                    "formatted": f"{th}h {tm}m" if th > 0 else f"{tm}m"
                })

            # Sort member topics by duration descending
            member_details.sort(key=lambda x: x["seconds"], reverse=True)

            groups.append({
                "label": group_label,
                "total_seconds": group_sec,
                "total_minutes": group_sec // 60,
                "formatted_duration": dur_str,
                "percentage": round(pct, 1),
                "topics": member_details
            })

        # Ensure any topic missed by LLM/rules is added as its own standalone group
        for t, sec in topic_distribution.items():
            if t not in covered_topics:
                h = sec // 3600
                m = (sec % 3600) // 60
                dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"
                pct = (sec / total_seconds * 100) if total_seconds > 0 else 0.0
                groups.append({
                    "label": t,
                    "total_seconds": sec,
                    "total_minutes": sec // 60,
                    "formatted_duration": dur_str,
                    "percentage": round(pct, 1),
                    "topics": [{
                        "name": t,
                        "seconds": sec,
                        "formatted": dur_str
                    }]
                })

        # Sort groups by total_seconds descending
        groups.sort(key=lambda g: g["total_seconds"], reverse=True)

        return {
            "total_seconds": total_seconds,
            "groups": groups
        }

    def _get_semantic_grouping_from_llm(self, topics: List[str]) -> Optional[Dict[str, List[str]]]:
        """Calls the LLM provider router to semantically cluster topics."""
        prompt = (
            "You are a computer science and academic curriculum categorization engine.\n"
            "Group the following list of study topic names into broader learning areas.\n\n"
            "STRICT RULES:\n"
            "1. Group semantically related topics (e.g. 'Python', 'Python Programming', 'Python Projects' -> 'Python').\n"
            "2. Combine genuinely related topics into broader learning areas; do not make a separate group for every input topic when related topics can be combined.\n"
            "3. Be conservative. Do not group unrelated topics just because they share a generic word (e.g. 'Java' and 'JavaScript' must remain separate).\n"
            "4. Assign a clean, concise title for each learning area (e.g. 'Python', 'Algorithms', 'Mathematics').\n"
            "5. Every topic in the input list must be included in exactly one group; use a single-topic group only when that topic has no genuinely related input topic.\n"
            "6. Output ONLY valid JSON in this exact structure with no surrounding commentary:\n"
            "{\n"
            '  "groups": [\n'
            '    {"label": "Area Name", "topics": ["Topic 1", "Topic 2"]}\n'
            "  ]\n"
            "}\n\n"
            f"INPUT TOPICS: {json.dumps(topics)}"
        )

        try:
            raw_response = self.router.generate_text(prompt)
            if not raw_response or raw_response.startswith("ERROR:"):
                return None

            # Extract JSON block
            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not json_match:
                return None

            data = json.loads(json_match.group(0))
            raw_groups = data.get("groups", [])
            if not isinstance(raw_groups, list):
                return None

            result: Dict[str, List[str]] = {}
            included = []
            normalized_labels = set()
            for g in raw_groups:
                if not isinstance(g, dict):
                    return None
                label = g.get("label", "")
                if not isinstance(label, str):
                    return None
                label = label.strip()
                normalized_label = label.casefold()
                if normalized_label in normalized_labels:
                    return None
                normalized_labels.add(normalized_label)
                t_list = g.get("topics", [])
                if not label or not isinstance(t_list, list) or not t_list:
                    return None
                if any(not isinstance(topic, str) for topic in t_list):
                    return None
                members = [topic.strip() for topic in t_list]
                if any(topic not in topics for topic in members):
                    return None
                result[label] = members
                included.extend(members)

            if result and len(included) == len(topics) and set(included) == set(topics):
                return result
        except Exception as e:
            logger.warning("Semantic grouping via LLM failed or returned malformed data (%s).", type(e).__name__)

        return None

    def _conservative_rule_grouping(self, topics: List[str]) -> Dict[str, List[str]]:
        """
        Conservative deterministic fallback grouping when AI is unavailable or offline.
        Groups topics that share identical key stems or prefixes.
        """
        modifiers = {
            "basics", "basic", "advanced", "intro", "introduction", "programming", "project", "projects",
            "homework", "assignment", "lab", "course", "tutorial", "practice", "study", "part", "chapter",
            "101", "102", "1", "2", "3", "i", "ii", "iii"
        }

        def extract_root(topic: str) -> str:
            words = [w for w in re.findall(r"\b\w+\b", topic.strip()) if w]
            significant = [w for w in words if w.lower() not in modifiers]
            if significant:
                return " ".join(significant)
            return topic.strip()

        groups: Dict[str, List[str]] = {}
        labels: Dict[str, str] = {}
        for topic in topics:
            root = extract_root(topic)
            key = root.casefold()
            if key not in groups:
                groups[key] = []
                labels[key] = root
            groups[key].append(topic)

        return {labels[key]: members for key, members in groups.items()}
