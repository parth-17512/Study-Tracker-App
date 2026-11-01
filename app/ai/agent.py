import logging
from typing import Dict, Any, List, Optional
from app.ai.tools import AITools
from app.ai.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class StudyCoachAgent:
    """
    Orchestrates the AI logic and safely limits its access to the application 
    via the AITools sandbox.
    """
    
    def __init__(self, provider: LLMProvider, tools: Optional[AITools] = None):
        self.tools = tools or AITools()
        self.provider = provider
        
    def get_available_tools(self) -> list:
        """Returns a JSON-serializable schema of all tools the LLM can call."""
        return [
            {
                "name": "get_today_stats",
                "description": "Get study duration, session count, and subjects studied today.",
                "parameters": {}
            },
            {
                "name": "get_week_stats",
                "description": "Get total study duration for the current trailing 7 days.",
                "parameters": {}
            },
            {
                "name": "get_week_by_week_stats",
                "description": "Get week-by-week study analysis for the last 4 weeks with dates and subject breakdowns.",
                "parameters": {
                    "num_weeks": "integer (optional, default 4)"
                }
            },
            {
                "name": "get_subject_stats",
                "description": "Get study duration breakdown by subject/topic, including most and least studied subjects.",
                "parameters": {
                    "start_date": "string YYYY-MM-DD (optional)",
                    "end_date": "string YYYY-MM-DD (optional)"
                }
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
            },
            {
                "name": "get_notes_today",
                "description": "Get all notes written or edited today.",
                "parameters": {}
            },
            {
                "name": "get_notes_by_date",
                "description": "Get all notes written or edited on a specific date (YYYY-MM-DD).",
                "parameters": {
                    "target_date": "string (format YYYY-MM-DD)"
                }
            },
            {
                "name": "get_notes_by_date_range",
                "description": "Get notes written or edited between start_date and end_date.",
                "parameters": {
                    "start_date": "string (YYYY-MM-DD)",
                    "end_date": "string (YYYY-MM-DD)"
                }
            },
            {
                "name": "list_notes",
                "description": "Get a list of all notes and folders the user has created.",
                "parameters": {}
            },
            {
                "name": "read_note",
                "description": "Read the entire content of a specific note by ID.",
                "parameters": {
                    "note_id": "integer"
                }
            },
            {
                "name": "search_notes",
                "description": "Search across all notes for a specific query.",
                "parameters": {
                    "query": "string"
                }
            },
            {
                "name": "get_note_chunks",
                "description": "Get note content split into smaller reading chunks by ID.",
                "parameters": {
                    "note_id": "integer"
                }
            }
        ]
        
    def execute_tool(self, tool_name: str, **kwargs) -> dict:
        """
        Safely routes a tool execution request from the LLM to the underlying 
        sandbox tools.
        """
        logger.info("AI Agent executing tool: %s", tool_name)
        
        try:
            if tool_name == "get_today_stats":
                return self.tools.get_today_stats()
            elif tool_name == "get_week_stats":
                return self.tools.get_week_stats()
            elif tool_name == "get_week_by_week_stats":
                num_weeks = int(kwargs.get("num_weeks", 4))
                return self.tools.get_week_by_week_stats(num_weeks)
            elif tool_name == "get_subject_stats":
                return self.tools.get_subject_stats(
                    start_date=kwargs.get("start_date"),
                    end_date=kwargs.get("end_date")
                )
            elif tool_name == "get_month_stats":
                return self.tools.get_month_stats()
            elif tool_name == "get_streak":
                return self.tools.get_streak()
            elif tool_name == "get_recent_sessions":
                limit = int(kwargs.get("limit", 5))
                return {"sessions": self.tools.get_recent_sessions(limit)}
            elif tool_name == "get_notes_today":
                return self.tools.get_notes_today()
            elif tool_name == "get_notes_by_date":
                return self.tools.get_notes_by_date(str(kwargs.get("target_date", "")))
            elif tool_name == "get_notes_by_date_range":
                return self.tools.get_notes_by_date_range(
                    str(kwargs.get("start_date", "")),
                    str(kwargs.get("end_date", ""))
                )
            elif tool_name == "list_notes":
                return self.tools.list_notes()
            elif tool_name == "read_note":
                return self.tools.read_note(int(kwargs.get("note_id", 0)))
            elif tool_name == "search_notes":
                return self.tools.search_notes(str(kwargs.get("query", "")))
            elif tool_name == "get_note_chunks":
                return self.tools.get_note_chunks(int(kwargs.get("note_id", 0)))
            elif tool_name == "get_goal_progress":
                return self.tools.get_goal_progress()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error("Error executing AI tool %s (%s).", tool_name, type(e).__name__)
            return {"error": f"Internal execution error: {str(e)}"}
            
    def chat(self, prompt: str) -> str:
        """Processes a natural language prompt using the configured LLM Provider."""
        schema = self.get_available_tools()
        return self.provider.generate_response(prompt, schema, self.execute_tool)

    def format_note(self, content: str) -> str:
        """
        Formats a user's markdown note according to strict preservation rules.
        """
        prompt = f"""You are a strict formatting assistant. Your job is to format the following markdown notes.
RULES:
1. Preserve the meaning of the user's notes.
2. Do not add facts.
3. Do not remove ideas.
4. Do not invent relationships.
5. Correct spelling and obvious grammar errors.
6. Correct numbering.
7. Correct indentation.
8. Improve structure only when supported by the existing content.
9. ONLY output the final formatted markdown. Do not include introductory or concluding conversational text.

ORIGINAL NOTES:
{content}
"""
        return self.provider.generate_response(prompt, [], lambda x, **kw: {})
