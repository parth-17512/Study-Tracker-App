import pytest
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.gemini import GeminiProvider

def test_mock_provider_fallback():
    provider = MockLLMProvider()
    
    def mock_callback(tool_name, **kwargs):
        if tool_name == "get_streak":
            return {"current_streak_days": 42}
        return {}
        
    response = provider.generate_response("What is my streak?", [], mock_callback)
    assert "[MOCK]" in response
    assert "42" in response

def test_gemini_provider_missing_key():
    provider = GeminiProvider("")
    response = provider.generate_response("Hello", [], lambda x: {})
    assert "ERROR" in response
    assert "API Key is not configured" in response
