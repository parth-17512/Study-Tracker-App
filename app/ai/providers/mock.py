from typing import List, Dict, Any, Tuple, Optional
from app.ai.providers.base import LLMProvider

class MockLLMProvider(LLMProvider):
    """
    A mock provider for local development, testing, and offline fallback.
    It simulates an LLM by answering based on keywords and invoking tool callbacks.
    """
    
    @property
    def provider_id(self) -> str:
        return "mock"

    @property
    def provider_name(self) -> str:
        return "Offline Mode (Mock Provider)"

    def is_available(self) -> Tuple[bool, str]:
        return True, "Offline mock provider is available."

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Returns deterministic response for offline generation."""
        p = prompt.lower()
        if "format" in p:
            # For note formatting, return the prompt's content section
            if "ORIGINAL NOTES:" in prompt:
                return prompt.split("ORIGINAL NOTES:")[-1].strip()
            return prompt.strip()
        return f"[Offline AI] Analysis based on your data:\n{prompt[:300]}"

    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        p = prompt.lower()
        
        if "streak" in p:
            data = execute_tool_callback("get_streak")
            streak = data.get("current_streak_days", 0)
            return f"[MOCK] Your current daily study streak is {streak} day{'s' if streak != 1 else ''}!"
            
        elif "today" in p:
            data = execute_tool_callback("get_today_stats")
            mins = data.get("total_minutes") or data.get("total_study_minutes", 0)
            count = data.get("session_count", 0)
            return f"[MOCK] Today you completed {count} session(s) totaling {mins} minutes of focus time."
            
        elif any(k in p for k in ["4 week", "week-by-week", "last 4", "past 4"]):
            data = execute_tool_callback("get_week_by_week_stats", num_weeks=4)
            weeks = data.get("weeks", [])
            lines = ["[MOCK] 4-Week Study Analysis:"]
            for w in weeks:
                dur = w.get("formatted_duration", "0m")
                lines.append(f"- {w.get('label', 'Week')}: {dur}")
            return "\n".join(lines)

        elif "week" in p:
            data = execute_tool_callback("get_week_stats")
            mins = data.get("total_study_minutes", 0)
            return f"[MOCK] You studied for {mins} minutes this week."
            
        elif "recent" in p:
            data = execute_tool_callback("get_recent_sessions")
            sessions = data.get("sessions", [])
            return f"[MOCK] Found {len(sessions)} recent study session(s)."

        elif "subject" in p or "topic" in p:
            data = execute_tool_callback("get_subject_stats")
            by_subj = data.get("by_subject", {})
            lines = ["[MOCK] Subject Distribution:"]
            for s, info in by_subj.items():
                lines.append(f"- {s}: {info.get('formatted_duration', '0m')}")
            return "\n".join(lines) if by_subj else "[MOCK] No subject records found."
            
        return "[MOCK] StudyTrack processed your request using local data."
