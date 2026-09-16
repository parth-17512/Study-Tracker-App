from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM providers.
    Ensures that StudyCoachAgent remains decoupled from specific APIs (like Gemini or OpenAI).
    """
    
    @abstractmethod
    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        """
        Takes a natural language prompt, a schema of available tools, and a callback 
        to execute a tool if the LLM decides to call one.
        
        Returns the final natural language response from the LLM.
        """
        pass
