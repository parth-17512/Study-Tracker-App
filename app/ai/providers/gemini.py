import logging
from typing import List, Dict, Any, Tuple, Optional
from app.ai.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    Official Google Gemini API provider implementation using google-genai.
    Supports structured text generation, native function calling, and model fallback.
    """
    
    def __init__(self, api_key: str):
        self.api_key = (api_key or "").strip()
        self.models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
        
    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def is_available(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "Google Gemini API Key is not configured. Add your API key in Settings."
        try:
            from google import genai
            return True, "Gemini API key configured."
        except ImportError:
            return False, "The 'google-genai' Python package is not installed."

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates text completion directly using Gemini models."""
        if not self.api_key:
            return "ERROR: Gemini API Key is not configured."

        try:
            from google import genai
            from google.genai import types
        except ImportError:
            return "ERROR: google-genai is not installed."

        client = genai.Client(api_key=self.api_key)
        last_error = None

        for model_name in self.models:
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt or "You are a helpful study tracking AI."
                ) if system_prompt else None

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = e
                err_str = str(e).upper()
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "QUOTA" in err_str:
                    logger.warning("Gemini quota exhausted for model %s.", model_name)
                    return f"ERROR: [QUOTA_EXHAUSTED] Gemini API quota reached: {e}"
                if self._is_model_unavailable(err_str):
                    logger.warning("Gemini model %s is unavailable. Trying fallback.", model_name)
                    continue
                break

        return f"ERROR: Failed to communicate with Gemini API: {last_error}"

    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        if not self.api_key:
            return "ERROR: Gemini API Key is not configured. Please add it in the Settings page."
            
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            logger.error("google-genai package is not installed.")
            return "ERROR: The 'google-genai' package is not installed. Please run 'pip install google-genai'."
            
        last_error = None
        for model_name in self.models:
            try:
                client = genai.Client(api_key=self.api_key)
                
                gemini_tools = []
                if tools_schema:
                    declarations = []
                    for tool in tools_schema:
                        declarations.append(
                            types.FunctionDeclaration(
                                name=tool["name"],
                                description=tool["description"],
                                parameters=types.Schema(
                                    type=types.Type.OBJECT,
                                    properties={} 
                                )
                            )
                        )
                    gemini_tools = [types.Tool(function_declarations=declarations)]
                    
                chat = client.chats.create(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        system_instruction="You are a helpful AI Study Coach. Answer questions accurately and concisely."
                    )
                )
                
                response = chat.send_message(prompt)
                
                if response.function_calls:
                    for function_call in response.function_calls:
                        tool_name = function_call.name
                        result = execute_tool_callback(tool_name)
                        response = chat.send_message(
                            types.Part.from_function_response(
                                name=tool_name,
                                response=result
                            )
                        )
                        
                if response and response.text:
                    return response.text.strip()
                return "I processed your request, but received an empty response from the model."
                
            except Exception as e:
                last_error = e
                err_str = str(e).upper()
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "QUOTA" in err_str:
                    logger.warning("Gemini quota exhausted on model %s.", model_name)
                    return f"ERROR: [QUOTA_EXHAUSTED] Gemini API quota reached: {e}"
                if self._is_model_unavailable(err_str):
                    logger.warning("Gemini model %s is unavailable. Trying fallback.", model_name)
                    continue
                break
                
        logger.error("Gemini API request failed (%s).", type(last_error).__name__ if last_error else "UnknownError")
        return f"ERROR: Failed to communicate with Gemini API. {str(last_error)}"

    @staticmethod
    def _is_model_unavailable(error: str) -> bool:
        return (
            "503" in error
            or "UNAVAILABLE" in error
            or "404" in error
            or "NOT_FOUND" in error
            or "NO LONGER AVAILABLE" in error
        )
