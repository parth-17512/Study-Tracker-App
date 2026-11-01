import json
import sys
import types
import urllib.error
from unittest.mock import MagicMock, patch

from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.ai.providers.router import FallbackProviderRouter


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

    response = provider.generate_response("Hello", [], lambda _tool: {})

    assert "ERROR" in response
    assert "API Key is not configured" in response


def test_gemini_uses_current_flash_model_and_falls_back_on_retired_model():
    provider = GeminiProvider("test-key")
    requested_models = []

    class FakeModels:
        def generate_content(self, model, contents, config=None):
            requested_models.append(model)
            if model == "gemini-3.8-flash":
                raise RuntimeError(
                    "404 NOT_FOUND: This model is no longer available to new users"
                )
            return types.SimpleNamespace(text="Gemini response")

    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = lambda **_kwargs: types.SimpleNamespace(models=FakeModels())
    fake_genai.types = types.SimpleNamespace(
        GenerateContentConfig=lambda **kwargs: kwargs
    )
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai

    with patch.dict(sys.modules, {"google": fake_google, "google.genai": fake_genai}):
        response = provider.generate_text("Hello")

    assert response == "Gemini response"
    assert requested_models == ["gemini-3.8-flash", "gemini-2.5-flash"]


def test_compatible_api_sends_auth_and_parses_reply():
    provider = OpenAICompatibleProvider(
        base_url="https://api.example.test/v1",
        api_key="test-api-key",
        model="free-chat-model",
        provider_label="Example",
    )
    body = json.dumps({
        "choices": [{"message": {"content": "Hosted response"}}]
    }).encode("utf-8")
    mock_response = MagicMock()
    mock_response.read.return_value = body
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as urlopen:
        result = provider.generate_text("Hello", "System instruction")

    request = urlopen.call_args.args[0]
    payload = json.loads(request.data.decode("utf-8"))
    assert request.full_url == "https://api.example.test/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-api-key"
    assert payload["messages"][0] == {
        "role": "system",
        "content": "System instruction",
    }
    assert result == "Hosted response"


def test_compatible_api_returns_quota_error_for_429():
    provider = OpenAICompatibleProvider(
        base_url="https://api.example.test/v1",
        api_key="test-api-key",
        model="model",
    )
    error = urllib.error.HTTPError(
        "https://api.example.test/v1/chat/completions",
        429,
        "Rate limited",
        {},
        None,
    )
    with patch("urllib.request.urlopen", side_effect=error):
        result = provider.generate_text("Hello")

    assert "[QUOTA_EXHAUSTED]" in result


def _router_config(**overrides):
    settings = {
        "llm_provider_priority": "gemini_first",
        "gemini_api_key": "test-gemini-key",
        "compatible_api_base_url": "https://api.example.test/v1",
        "compatible_api_key": "test-compatible-key",
        "compatible_api_model": "free-model",
        "cloud_consent": True,
    }
    settings.update(overrides)
    config = MagicMock()
    config.get.side_effect = lambda key, default=None: settings.get(key, default)
    return config


def test_router_falls_back_from_gemini_to_compatible_api():
    router = FallbackProviderRouter(config_manager=_router_config())
    router.gemini.is_available = lambda: (True, "Ready")
    router.gemini.generate_text = lambda *_args, **_kwargs: (
        "ERROR: [QUOTA_EXHAUSTED] Gemini quota reached"
    )
    router.compatible_api.is_available = lambda: (True, "Ready")
    router.compatible_api.generate_text = lambda *_args, **_kwargs: (
        "Response from compatible API."
    )

    result = router.generate_text("Explain polymorphism")

    assert result == "Response from compatible API."
    assert router.last_used_provider_name == router.compatible_api.provider_name


def test_router_uses_only_configured_provider_order():
    router = FallbackProviderRouter(config_manager=_router_config())

    assert [provider.provider_id for provider in router.get_provider_priority_list()] == [
        "gemini",
        "openai_compatible",
    ]

    router.refresh_config()
    router.config = _router_config(llm_provider_priority="compatible_api_first")
    router.refresh_config()
    assert [
        provider.provider_id for provider in router.get_provider_priority_list()
    ] == ["openai_compatible", "gemini"]


def test_router_does_not_send_study_context_without_consent():
    router = FallbackProviderRouter(
        config_manager=_router_config(cloud_consent=False)
    )
    router.gemini.generate_text = MagicMock(return_value="Cloud response")
    router.compatible_api.generate_text = MagicMock(return_value="Cloud response")

    result = router.generate_text("Private study notes")

    assert "All configured LLM providers failed" in result
    router.gemini.generate_text.assert_not_called()
    router.compatible_api.generate_text.assert_not_called()


def test_router_reports_failures_without_unconfigured_provider_fallback():
    router = FallbackProviderRouter(
        config_manager=_router_config(
            llm_provider_priority="gemini_only",
            compatible_api_key="",
        )
    )
    router.gemini.is_available = lambda: (False, "Gemini key unavailable")

    result = router.generate_response(
        "Use my study data", [], lambda *_args, **_kwargs: {}
    )

    assert "All configured LLM providers failed" in result
    assert "Gemini key unavailable" in result
    assert "[MOCK]" not in result
    assert router.last_used_provider_name is None
