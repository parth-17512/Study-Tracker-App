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
        self.model_name = "gemini-2.5-flash"
        
    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        if not self.api_key:
            return "ERROR: Gemini API Key is not configured. Please add it in the Settings page."
            
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            logger.error("google-genai package is not installed.")
            return "ERROR: The 'google-genai' package is not installed. Please run 'pip install google-genai'."
            
        try:
            client = genai.Client(api_key=self.api_key)
            
            # Map our simple JSON tools_schema to Gemini's expected FunctionDeclarations
            gemini_tools = []
            if tools_schema:
                declarations = []
                for tool in tools_schema:
                    # Our simplified schema has 'name', 'description', 'parameters'
                    # Convert to Gemini FunctionDeclaration
                    declarations.append(
                        types.FunctionDeclaration(
                            name=tool["name"],
                            description=tool["description"],
                            parameters=types.Schema(
                                type=types.Type.OBJECT,
                                properties={} # We assume no strict parameters for these basic tools
                            )
                        )
                    )
                gemini_tools = [types.Tool(function_declarations=declarations)]
                
            # Initialize a chat session
            # We use chat so it can handle multi-turn if it decides to call a function
            chat = client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    tools=gemini_tools,
                    system_instruction="You are a helpful AI Study Coach. You have access to tools that can pull data about the user's study habits. Use them to answer questions accurately and concisely."
                )
            )
            
            # Send the initial prompt
            response = chat.send_message(prompt)
            
            # Check if Gemini decided to call a function
            if response.function_calls:
                for function_call in response.function_calls:
                    tool_name = function_call.name
                    # Call our sandbox callback
                    result = execute_tool_callback(tool_name)
                    
                    # Send the result back to Gemini so it can formulate an answer
                    # According to the SDK, we send it back as a FunctionResponse
                    response = chat.send_message(
                        types.Part.from_function_response(
                            name=tool_name,
                            response=result
                        )
                    )
                    
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return f"ERROR: Failed to communicate with Gemini API. {str(e)}"
