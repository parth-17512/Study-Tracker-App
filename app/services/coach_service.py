import re
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from app.services.analytics_service import AnalyticsService
from app.services.note_service import NoteService
from app.ai.agent import StudyCoachAgent
from app.utils.time_utils import to_local_time

logger = logging.getLogger(__name__)

class CoachService:
    """
    Unified AI Coach Retrieval and Response Service.
    Accurately routes queries to structured study analytics and note repositories,
    constructs factual, bounded contexts, and guarantees grounded, non-empty responses.
    """

    def __init__(self, agent: StudyCoachAgent, analytics_service: Optional[AnalyticsService] = None, note_service: Optional[NoteService] = None, tz=None):
        self.agent = agent
        self.analytics = analytics_service or AnalyticsService()
        self.notes = note_service or NoteService()
        self.tz = tz or datetime.now().astimezone().tzinfo

    def process_query(self, query: str) -> str:
        """
        Main entrypoint: parses intent, retrieves factual data, invokes the agent,
        and provides grounded fallback if the provider fails or returns empty.
        """
        q = query.strip()
        if not q:
            return "Please ask a question about your study habits or notes."

        lower_q = q.lower()
        now = datetime.now(timezone.utc)
        local_now = to_local_time(now, tz=self.tz)
        today = local_now.date()

        # Step 1: Detect intent and relevant domains
        wants_notes = self._is_note_query(lower_q)
        wants_analytics = self._is_analytics_query(lower_q)

        # If neither keyword was explicitly matched, check for open questions
        if not wants_notes and not wants_analytics:
            # Check if query asks about notes or study activity implicitly
            if any(w in lower_q for w in ["what", "how", "when", "show", "tell", "summary", "analysis"]):
                # By default, retrieve today's context or route generally
                wants_analytics = True
                wants_notes = True

        retrieved_context_parts = []
        deterministic_response_parts = []

        # Step 2: Retrieve Study History / Analytics
        analytics_data = None
        if wants_analytics:
            analytics_data = self._retrieve_analytics(lower_q, today, local_now)
            if analytics_data:
                retrieved_context_parts.append(analytics_data["context_text"])
                deterministic_response_parts.append(analytics_data["summary_text"])

        # Step 3: Retrieve Notes
        notes_data = None
        if wants_notes:
            notes_data = self._retrieve_notes(lower_q, today, local_now)
            if notes_data:
                retrieved_context_parts.append(notes_data["context_text"])
                deterministic_response_parts.append(notes_data["summary_text"])

        # If both retrieved data sources are empty, inform user what was checked
        if not retrieved_context_parts:
            # Fall back to general agent chat with available tools
            try:
                resp = self.agent.chat(query)
                if resp and resp.strip() and not resp.startswith("ERROR:"):
                    return resp
            except Exception as e:
                logger.error("General agent chat failed (%s).", type(e).__name__)
            return "I couldn't find any relevant study records or notes matching your query. Try asking about your study time today, a 4-week analysis, or notes written on a specific date."

        # Step 4: Construct bounded prompt with retrieved facts
        context_block = "\n\n".join(retrieved_context_parts)
        prompt = (
            f"You are the StudyTrack AI Study Coach. Answer the user's question accurately and helpfully.\n\n"
            f"RULES:\n"
            f"1. Base your answer strictly on the verified DATA CONTEXT provided below.\n"
            f"2. Never invent study sessions, hours, subjects, or notes.\n"
            f"3. If a period shows 0 study time or no notes were found, state that clearly.\n"
            f"4. Format your answer with clear markdown (bolding, bullet points, headers).\n\n"
            f"DATA CONTEXT:\n{context_block}\n\n"
            f"User Question: {q}\n"
        )

        # Step 5: Call LLM Provider
        try:
            llm_response = self.agent.chat(prompt)
            if llm_response and llm_response.strip() and not llm_response.startswith("ERROR:"):
                return llm_response.strip()
            else:
                logger.warning("LLM returned an empty or error response; using deterministic fallback.")
        except Exception as e:
            logger.error("LLM request failed (%s); using deterministic fallback.", type(e).__name__)

        # Step 6: Grounded Deterministic Fallback (Guarantees non-empty, factual response)
        fallback = "\n\n".join(deterministic_response_parts)
        return fallback

    def _is_note_query(self, lower_q: str) -> bool:
        note_keywords = ["note", "notes", "wrote", "written", "write", "folder", "document", "read note", "search notes"]
        return any(k in lower_q for k in note_keywords)

    def _is_analytics_query(self, lower_q: str) -> bool:
        stat_keywords = [
            "week", "weeks", "today", "yesterday", "study", "studied", "time", "hour", "hours", "minute", "minutes",
            "session", "sessions", "streak", "subject", "subjects", "topic", "topics", "analysis", "analytics",
            "stat", "stats", "history", "distribution", "least", "most", "progress", "goal", "duration"
        ]
        return any(k in lower_q for k in stat_keywords)

    def _retrieve_analytics(self, lower_q: str, today: date, local_now: datetime) -> Optional[Dict[str, str]]:
        # Check for week-by-week / 4-week analysis
        if any(p in lower_q for p in ["week-by-week", "week by week", "4 week", "four week", "last 4", "past 4"]):
            weeks = self.analytics.get_week_by_week_analysis(num_weeks=4, reference_dt=local_now, tz=self.tz)
            lines = ["### Study Activity: 4-Week Analysis (Monday to Sunday)"]
            summary_lines = ["### 📊 4-Week Study Analysis"]

            for w in weeks:
                label = w["label"]
                rel = w["relative_label"]
                dur = w["formatted_duration"]
                count = w["session_count"]

                if w["is_zero_study"] or not w["has_data"]:
                    status_text = "0m (No study activity logged)"
                else:
                    status_text = f"{dur} across {count} session{'s' if count != 1 else ''}"

                lines.append(f"- **{label}** ({rel}): {status_text}")
                summary_lines.append(f"- **{label}** ({rel}): {status_text}")

                if w["subjects"]:
                    subj_str = ", ".join([f"{s}: {m//60}m" for s, m in w["subjects"].items() if m > 0])
                    lines.append(f"  - Subjects: {subj_str}")
                    summary_lines.append(f"  - Subjects: {subj_str}")

            return {
                "context_text": "\n".join(lines),
                "summary_text": "\n".join(summary_lines)
            }

        query_dates = self._extract_query_dates(lower_q)
        if len(query_dates) >= 4 and any(
            word in lower_q for word in ["compare", "comparison", "change", "difference"]
        ):
            start1, end1, start2, end2 = query_dates[:4]
            if end1 < start1:
                start1, end1 = end1, start1
            if end2 < start2:
                start2, end2 = end2, start2
            first = self.analytics.get_date_range_summary(start1, end1, tz=self.tz)
            second = self.analytics.get_date_range_summary(start2, end2, tz=self.tz)
            difference = second["total_seconds"] - first["total_seconds"]
            percentage = (
                difference / first["total_seconds"] * 100
                if first["total_seconds"] else (100.0 if second["total_seconds"] else 0.0)
            )
            change_text = (
                f"{abs(difference) // 3600}h {(abs(difference) % 3600) // 60}m "
                f"{'more' if difference > 0 else 'less' if difference < 0 else 'the same'} "
                f"({abs(percentage):.1f}%)."
            )
            text = (
                f"Study time from {start1.isoformat()} through {end1.isoformat()} was "
                f"{first['formatted_duration']}; from {start2.isoformat()} through "
                f"{end2.isoformat()} it was {second['formatted_duration']}. "
                f"The second period had {change_text}"
            )
            return {"context_text": text, "summary_text": f"### Study Time Comparison\n- {text}"}

        if len(query_dates) >= 2:
            start_date, end_date = query_dates[:2]
            if end_date < start_date:
                start_date, end_date = end_date, start_date
            summary = self.analytics.get_date_range_summary(start_date, end_date, tz=self.tz)
            subjects = ", ".join(
                f"{name}: {seconds // 60}m" for name, seconds in summary["subjects"].items()
            ) or "None"
            status = (
                f"{summary['formatted_duration']} across {summary['session_count']} completed sessions"
                if summary["has_data"] else "0m (No study activity logged)"
            )
            text = (
                f"Study activity from {start_date.isoformat()} through {end_date.isoformat()}: "
                f"{status}. Subjects: {subjects}."
            )
            return {"context_text": text, "summary_text": f"### Study Activity\n- {text}"}

        if len(query_dates) == 1:
            target_date = query_dates[0]
            summary = self.analytics.get_date_range_summary(target_date, target_date, tz=self.tz)
            subjects = ", ".join(
                f"{name}: {seconds // 60}m" for name, seconds in summary["subjects"].items()
            ) or "None"
            status = (
                f"{summary['formatted_duration']} across {summary['session_count']} completed sessions"
                if summary["has_data"] else "0m (No study activity logged)"
            )
            text = (
                f"Study activity on {target_date.isoformat()}: {status}. "
                f"Subjects: {subjects}."
            )
            return {"context_text": text, "summary_text": f"### Study Activity\n- {text}"}

        # Check for streak
        if "streak" in lower_q:
            streak = self.analytics.calculate_current_streak(local_now)
            text = f"Current Daily Study Streak: {streak} day{'s' if streak != 1 else ''}."
            return {
                "context_text": f"### Streak\n{text}",
                "summary_text": f"🔥 **Current Streak:** {streak} day{'s' if streak != 1 else ''}."
            }

        if "this week" in lower_q or "current week" in lower_q or "last week" in lower_q:
            this_monday = today - timedelta(days=today.weekday())
            if "last week" in lower_q and "this week" not in lower_q:
                start_date = this_monday - timedelta(days=7)
                end_date = this_monday - timedelta(days=1)
            else:
                start_date = this_monday
                end_date = today
            summary = self.analytics.get_date_range_summary(start_date, end_date, tz=self.tz)
            subjects = ", ".join(
                f"{name}: {seconds // 60}m" for name, seconds in summary["subjects"].items()
            ) or "None"
            status = (
                f"{summary['formatted_duration']} across {summary['session_count']} completed sessions"
                if summary["has_data"] else "0m (No study activity logged)"
            )
            text = (
                f"Study activity from {start_date.isoformat()} through {end_date.isoformat()}: "
                f"{status}. Subjects: {subjects}."
            )
            return {"context_text": text, "summary_text": f"### Study Activity This Week\n- {text}"}

        # Check for today's study stats
        if "today" in lower_q:
            summary = self.analytics.get_today_summary(reference_dt=local_now, tz=self.tz)
            dur = summary["formatted_duration"]
            count = summary["session_count"]
            subj_list = [f"{s}: {m//60}m" for s, m in summary["subjects"].items()]
            subj_str = ", ".join(subj_list) if subj_list else "None"

            lines = [
                f"### Study History for Today ({today.strftime('%Y-%m-%d')}):",
                f"- Total Study Time: {dur}",
                f"- Sessions Completed: {count}",
                f"- Subjects Studied: {subj_str}"
            ]
            summary_text = (
                f"### ⏱️ Today's Study Summary ({today.strftime('%b %d, %Y')})\n"
                f"- **Total Focus Time:** {dur}\n"
                f"- **Completed Sessions:** {count}\n"
                f"- **Subjects:** {subj_str}"
            )
            return {
                "context_text": "\n".join(lines),
                "summary_text": summary_text
            }

        # Check for subject breakdown / most / least studied
        if any(w in lower_q for w in ["subject", "topic", "most", "least", "distribution"]):
            breakdown = self.analytics.get_subject_breakdown()
            lines = ["### Study Time by Subject:"]
            summary_lines = ["### 📚 Subject Distribution"]

            if not breakdown["by_subject"]:
                lines.append("No study sessions recorded yet.")
                summary_lines.append("No study sessions recorded yet.")
            else:
                for subj, data in breakdown["by_subject"].items():
                    line = f"- **{subj}**: {data['formatted_duration']} ({data['percentage']}%, {data['session_count']} sessions)"
                    lines.append(line)
                    summary_lines.append(line)

                if breakdown["most_studied"]:
                    m = breakdown["most_studied"]
                    lines.append(f"Most studied subject: {m['subject']} ({m['formatted_duration']})")
                    summary_lines.append(f"\n- **Most Studied:** {m['subject']} ({m['formatted_duration']})")
                if breakdown["least_studied"]:
                    l = breakdown["least_studied"]
                    lines.append(f"Least studied subject: {l['subject']} ({l['formatted_duration']})")
                    summary_lines.append(f"- **Least Studied:** {l['subject']} ({l['formatted_duration']})")

            return {
                "context_text": "\n".join(lines),
                "summary_text": "\n".join(summary_lines)
            }

        # General recent study summary
        stats = self.analytics.get_summary_stats()
        recent = self.analytics.get_recent_sessions(limit=5)
        lines = [
            f"### Overall Study Summary:",
            f"- Total Sessions: {stats['total_sessions']}",
            f"- Total Study Time: {stats['total_seconds'] // 3600}h {(stats['total_seconds'] % 3600) // 60}m",
            f"Recent Sessions:"
        ]
        summary_lines = ["### ⏱️ Study History Overview"]
        if not recent:
            lines.append("No completed sessions found.")
            summary_lines.append("No completed sessions recorded.")
        else:
            for s in recent:
                t = s.topic or "Focus Session"
                m = (s.duration_seconds or 0) // 60
                d_str = s.start_time.strftime("%b %d") if s.start_time else "Unknown date"
                lines.append(f"- {d_str}: {t} ({m}m)")
                summary_lines.append(f"- **{d_str}:** {t} ({m}m)")

        return {
            "context_text": "\n".join(lines),
            "summary_text": "\n".join(summary_lines)
        }

    @staticmethod
    def _extract_query_dates(lower_q: str) -> List[date]:
        """Parse explicit ISO dates for deterministic, timezone-aware retrieval."""
        dates = []
        for value in re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", lower_q):
            try:
                parsed = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                logger.info("Ignored malformed ISO date in Coach query.")
                continue
            if parsed not in dates:
                dates.append(parsed)
        return dates

    def _retrieve_notes(self, lower_q: str, today: date, local_now: datetime) -> Optional[Dict[str, str]]:
        # Detect exact date or date ranges
        target_date = None
        date_label = None

        if "today" in lower_q:
            target_date = today
            date_label = f"today ({today.strftime('%b %d, %Y')})"
        elif "yesterday" in lower_q:
            target_date = today - timedelta(days=1)
            date_label = f"yesterday ({target_date.strftime('%b %d, %Y')})"
        else:
            query_dates = self._extract_query_dates(lower_q)
            if len(query_dates) >= 2:
                start_date, end_date = query_dates[:2]
                if end_date < start_date:
                    start_date, end_date = end_date, start_date
                date_label = f"from {start_date.strftime('%b %d, %Y')} through {end_date.strftime('%b %d, %Y')}"
                notes = self.notes.get_notes_by_date_range(start_date, end_date, tz=self.tz)
                return self._format_note_results(notes, date_label)
            if query_dates:
                target_date = query_dates[0]
                date_label = f"on {target_date.strftime('%b %d, %Y')}"

        # Perform date retrieval if date target identified
        if target_date:
            notes = self.notes.get_notes_by_date(target_date, tz=self.tz)
            return self._format_note_results(notes, date_label)

        # Check for keyword search in notes
        # Extract probable search topic
        topic_match = re.search(r"notes?\s+(?:on|about|for|regarding)\s+([a-zA-Z0-9_\- ]+)", lower_q)
        query_term = topic_match.group(1).strip() if topic_match else None
        if not query_term:
            # Check if user asked e.g. "search notes python"
            search_match = re.search(r"search\s+notes?\s+(?:for\s+)?([a-zA-Z0-9_\- ]+)", lower_q)
            if search_match:
                query_term = search_match.group(1).strip()

        if query_term:
            notes = self.notes.search_notes(query_term)
            if not notes:
                msg = f"No notes matching query '{query_term}' were found."
                return {
                    "context_text": f"### Notes Search\n{msg}",
                    "summary_text": f"📝 {msg}"
                }
            lines = [f"### Notes matching '{query_term}' ({len(notes)} found):"]
            summary_lines = [f"### 📝 Notes matching '{query_term}':"]
            for n in notes[:5]:
                snippet = (n.content[:200] + "...") if n.content and len(n.content) > 200 else (n.content or "")
                folder = n.parent.name if n.parent else "Root"
                lines.append(f"- **{n.name}** (Folder: {folder}, ID: {n.id}):\n  {snippet}")
                summary_lines.append(f"- **{n.name}** (Folder: `{folder}`):\n  {snippet}")

            return {
                "context_text": "\n".join(lines),
                "summary_text": "\n".join(summary_lines)
            }

        # List recent notes only when the user asks for notes without a date or topic.
        recent_notes = self.notes.get_recent_notes(limit=5)
        if not recent_notes:
            return {
                "context_text": "### Notes Search\nNo notes currently exist in the database.",
                "summary_text": "📝 You haven't created any notes yet."
            }

        lines = ["### Recent Notes in Notebook:"]
        summary_lines = ["### 📝 Recent Notes"]
        for note in recent_notes:
            folder = note.parent.name if note.parent else "Root"
            created = to_local_time(note.created_at, tz=self.tz)
            updated = to_local_time(note.updated_at, tz=self.tz)
            lines.append(
                f"- **{note.name}** (Folder: {folder}, created: {created.isoformat() if created else 'unknown'}, "
                f"updated: {updated.isoformat() if updated else 'unknown'}, ID: {note.id})"
            )
            summary_lines.append(f"- **{note.name}** (Folder: `{folder}`)")

        return {
            "context_text": "\n".join(lines),
            "summary_text": "\n".join(summary_lines)
        }

    @staticmethod
    def _format_note_results(notes: List[Dict[str, Any]], date_label: str) -> Dict[str, str]:
        if not notes:
            message = f"No notes were written or edited {date_label}."
            return {
                "context_text": f"### Notes Search\n{message}",
                "summary_text": f"📝 **Notes {date_label}:**\n{message}",
            }

        selected_notes = notes[:10]
        lines = [f"### Notes written or edited {date_label} ({len(notes)} found):"]
        summary_lines = [f"### 📝 Notes {date_label}"]
        total_chars = 0
        for note in selected_notes:
            content = note.get("content") or "(Empty note)"
            remaining = max(0, 4000 - total_chars)
            snippet = content[:min(800, remaining)]
            total_chars += len(snippet)
            if len(content) > len(snippet):
                snippet += "..."
            folder = note.get("folder", "Root")
            created = note.get("created_at") or "unknown"
            updated = note.get("updated_at") or "unknown"
            details = f"Folder: {folder}; created: {created}; updated: {updated}"
            lines.append(f"- **{note['name']}** ({details}, ID: {note['id']}):\n  {snippet}")
            summary_lines.append(f"- **{note['name']}** ({details}):\n  {snippet}")
            if total_chars >= 4000:
                break

        if len(notes) > len(selected_notes):
            lines.append(f"- Context limited to {len(selected_notes)} of {len(notes)} matching notes.")

        return {
            "context_text": "\n".join(lines),
            "summary_text": "\n".join(summary_lines)
        }
