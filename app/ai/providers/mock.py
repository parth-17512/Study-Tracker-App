import logging
from typing import List, Dict, Any
from app.ai.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class MockLLMProvider(LLMProvider):
    """
    A mock provider for local development and testing when an API key is not available.
    It simulates an LLM by checking for simple keywords and invoking the tool callback.
    """
    
    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        logger.info(f"MockLLMProvider processing prompt: '{prompt}'")
        
        p = prompt.lower()
        response = ""
        
        if "streak" in p:
            data = execute_tool_callback("get_streak")
            streak = data.get("current_streak_days", 0)
            response = f"[MOCK] I called the 'get_streak' tool. Your current streak is {streak} days!"
            
        elif "today" in p:
            data = execute_tool_callback("get_today_stats")
            mins = data.get("total_study_minutes", 0)
            response = f"[MOCK] I called the 'get_today_stats' tool. You have studied for {mins} minutes today."
            
        elif "week" in p:
            data = execute_tool_callback("get_week_stats")
            mins = data.get("total_study_minutes", 0)
            best = data.get("best_day", "Unknown")
            response = f"[MOCK] I called the 'get_week_stats' tool. You studied {mins} minutes this week. Best day: {best}."
            
        elif "recent" in p:
            data = execute_tool_callback("get_recent_sessions")
            sessions = data.get("sessions", [])
            count = len(sessions)
            response = f"[MOCK] I called the 'get_recent_sessions' tool. Found {count} recent sessions."
            
        else:
            response = "[MOCK] I am a mock AI. I couldn't map your query to a tool. Try asking about your 'streak', 'today', 'week', or 'recent' sessions."
            
        return response
