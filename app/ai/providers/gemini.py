import logging
from typing import List, Dict, Any
from app.ai.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    Official Google Gemini API provider implementation using google-genai.
    Supports native function calling to securely access application tools.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # We will try the newer model, and fallback if it's unavailable
        self.models = ["gemini-3.6-flash", "gemini-3.5-flash"]
        
    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        if not self.api_key:
            return "ERROR: Gemini API Key is not configured. Please add it in the Settings page."
            
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            logger.error("google-genai package is not installed.")
            return "ERROR: The 'google-genai' package is not installed. Please run 'pip install google-genai'."
            
        # Try models in order until one succeeds
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
                        system_instruction="You are a helpful AI Study Coach. You have access to tools that can pull data about the user's study habits. Use them to answer questions accurately and concisely."
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
                        
                return response.text
                
            except Exception as e:
                last_error = e
                # If it's a 503 Unavailable, log it and try the next model
                if "503" in str(e) or "UNAVAILABLE" in str(e).upper():
                    logger.warning(f"Model {model_name} is unavailable. Trying fallback.")
                    continue
                # If it's some other error (like bad credentials), stop immediately
                break
                
        logger.error(f"Gemini API Error: {last_error}")
        return f"ERROR: Failed to communicate with Gemini API. {str(last_error)}"
