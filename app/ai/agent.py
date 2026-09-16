import logging
from typing import Dict, Any
from app.ai.tools import AITools
from app.ai.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class StudyCoachAgent:
    """
    Orchestrates the AI logic and safely limits its access to the application 
    via the AITools sandbox.
    """
    
    def __init__(self, provider: LLMProvider):
        self.tools = AITools()
        self.provider = provider
        
    def get_available_tools(self) -> list:
        """Returns a JSON-serializable schema of all tools the LLM can call."""
        return [
            {
                "name": "get_today_stats",
                "description": "Get study duration and session count for today.",
                "parameters": {}
            },
            {
                "name": "get_week_stats",
                "description": "Get total study duration for the current week.",
                "parameters": {}
            },
            {
                "name": "get_streak",
                "description": "Get the user's current daily study streak.",
                "parameters": {}
            },
            {
                "name": "get_recent_sessions",
                "description": "Get a list of the most recent study sessions.",
                "parameters": {
                    "limit": "integer (optional, default 5)"
                }
            }
        ]
        
    def execute_tool(self, tool_name: str, **kwargs) -> dict:
        """
        Safely routes a tool execution request from the LLM to the underlying 
        sandbox tools.
        """
        logger.info(f"AI Agent executing tool: {tool_name} with args: {kwargs}")
        
        try:
            if tool_name == "get_today_stats":
                return self.tools.get_today_stats()
            elif tool_name == "get_week_stats":
                return self.tools.get_week_stats()
            elif tool_name == "get_month_stats":
                return self.tools.get_month_stats()
            elif tool_name == "get_streak":
                return self.tools.get_streak()
            elif tool_name == "get_recent_sessions":
                limit = kwargs.get("limit", 5)
                return {"sessions": self.tools.get_recent_sessions(limit)}
            elif tool_name == "get_subject_stats":
                return self.tools.get_subject_stats()
            elif tool_name == "get_goal_progress":
                return self.tools.get_goal_progress()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing AI tool {tool_name}: {e}")
            return {"error": f"Internal execution error: {str(e)}"}
            
    def chat(self, prompt: str) -> str:
        """Processes a natural language prompt using the configured LLM Provider."""
        schema = self.get_available_tools()
        return self.provider.generate_response(prompt, schema, self.execute_tool)
