from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM providers.
    Ensures that StudyCoachAgent, Subject Grouping, and Analytics remain decoupled
    from specific LLM backends (Gemini, compatible APIs, Mock).
    """
    
    @property
    def provider_id(self) -> str:
        return "base"

    @property
    def provider_name(self) -> str:
        return "Base LLM Provider"

    def is_available(self) -> Tuple[bool, str]:
        """
        Checks whether the provider is currently reachable, configured, and ready to serve.
        Returns:
            (True, "Available / Model details") if healthy.
            (False, "Setup guidance or error details") if unavailable.
        """
        return True, "Ready"

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates standard text (used for formatting, summarization, subject grouping).
        """
        return self.generate_response(prompt, [], lambda x, **kw: {})

    @abstractmethod
    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        """
        Takes a natural language prompt, a schema of available tools, and a callback 
        to execute a tool if the LLM decides to call one.
        Returns the final natural language response from the LLM.
        """
        pass
