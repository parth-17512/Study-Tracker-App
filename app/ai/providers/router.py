import logging
from typing import List, Dict, Any, Tuple, Optional
from app.config.config_manager import ConfigManager
from app.ai.providers.base import LLMProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)

class FallbackProviderRouter(LLMProvider):
    """
    Configurable fallback between Gemini and OpenAI-compatible hosted APIs.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
        self.last_used_provider_name: Optional[str] = None
        self._init_providers()

    def _init_providers(self):
        gemini_api_key = self.config.get("gemini_api_key", "").strip()

        self.gemini = GeminiProvider(api_key=gemini_api_key)
        self.compatible_api = OpenAICompatibleProvider(
            base_url=self.config.get("compatible_api_base_url", ""),
            api_key=self.config.get("compatible_api_key", ""),
            model=self.config.get("compatible_api_model", ""),
            provider_label=self.config.get("compatible_api_label", "Compatible API"),
            timeout=int(self.config.get("compatible_api_timeout", 60)),
        )

    def refresh_config(self):
        """Reloads providers with current configuration."""
        self._init_providers()

    @property
    def provider_id(self) -> str:
        return "router"

    @property
    def provider_name(self) -> str:
        return f"Router (Last: {self.last_used_provider_name or 'None'})"

    def get_provider_priority_list(self) -> List[LLMProvider]:
        """Resolves ordered list of providers based on user settings."""
        priority_setting = self.config.get("llm_provider_priority", "gemini_first")
        cloud_consent = self.config.get("cloud_consent", False)
        if not cloud_consent:
            return []

        configured = {
            "gemini": self.gemini if self.gemini.api_key else None,
            "compatible_api": (
                self.compatible_api
                if self.compatible_api.api_key
                and self.compatible_api.base_url
                and self.compatible_api.model
                else None
            ),
        }
        order = {
            "gemini_first": ("gemini", "compatible_api"),
            "compatible_api_first": ("compatible_api", "gemini"),
            "gemini_only": ("gemini",),
            "compatible_api_only": ("compatible_api",),
        }.get(priority_setting, ("gemini", "compatible_api"))
        return [configured[name] for name in order if configured[name] is not None]

    def is_available(self) -> Tuple[bool, str]:
        providers = self.get_provider_priority_list()
        for p in providers:
            avail, msg = p.is_available()
            if avail:
                return True, f"Active provider: {p.provider_name} ({msg})"
        return False, "No LLM providers are currently available."

    def get_providers_status(self) -> Dict[str, Dict[str, Any]]:
        """Returns comprehensive diagnostic info for the settings UI."""
        self.refresh_config()

        gemini_avail, gemini_msg = self.gemini.is_available()
        compatible_avail, compatible_msg = self.compatible_api.is_available()

        return {
            "gemini": {
                "available": gemini_avail,
                "message": gemini_msg,
                "has_key": bool(self.gemini.api_key)
            },
            "compatible_api": {
                "available": compatible_avail,
                "message": compatible_msg,
                "configured_model": self.compatible_api.model,
                "base_url": self.compatible_api.base_url,
                "has_key": bool(self.compatible_api.api_key),
            },
        }

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Executes text generation across providers in priority order with automatic fallback."""
        self.last_used_provider_name = None
        providers = self.get_provider_priority_list()
        errors = []

        for p in providers:
            avail, status_msg = p.is_available()
            if not avail:
                logger.info(f"Skipping {p.provider_name}: {status_msg}")
                errors.append(f"{p.provider_name}: {status_msg}")
                continue

            try:
                logger.info(f"Attempting generation with {p.provider_name}...")
                resp = p.generate_text(prompt, system_prompt)

                # Check for quota or connection failure strings
                if resp and not resp.startswith("ERROR:"):
                    self.last_used_provider_name = p.provider_name
                    logger.info(f"Successfully generated response with {p.provider_name}")
                    return resp
                else:
                    logger.warning("Provider %s returned an error response.", p.provider_name)
                    errors.append(f"{p.provider_name}: {resp}")
            except Exception as e:
                logger.warning("Provider %s failed (%s).", p.provider_name, type(e).__name__)
                errors.append(f"{p.provider_name}: {str(e)}")

        # If all fail, return actionable message
        err_details = "\n".join([f"- {e}" for e in errors]) or "- No provider is configured or permitted."
        return (
            f"All configured LLM providers failed to generate a response:\n"
            f"{err_details}\n\n"
            f"Configure Gemini or a compatible API key and allow cloud context in Settings."
        )

    def generate_response(self, prompt: str, tools_schema: List[Dict[str, Any]], execute_tool_callback: callable) -> str:
        """Executes conversational chat across providers in priority order with automatic fallback."""
        self.last_used_provider_name = None
        providers = self.get_provider_priority_list()
        errors = []

        for p in providers:
            avail, status_msg = p.is_available()
            if not avail:
                logger.info(f"Skipping {p.provider_name}: {status_msg}")
                errors.append(f"{p.provider_name}: {status_msg}")
                continue

            try:
                logger.info(f"Attempting chat with {p.provider_name}...")
                resp = p.generate_response(prompt, tools_schema, execute_tool_callback)

                if resp and not resp.startswith("ERROR:"):
                    self.last_used_provider_name = p.provider_name
                    logger.info(f"Successfully processed chat with {p.provider_name}")
                    return resp
                else:
                    logger.warning("Provider %s returned an error response.", p.provider_name)
                    errors.append(f"{p.provider_name}: {resp}")
            except Exception as e:
                logger.warning("Provider %s failed (%s).", p.provider_name, type(e).__name__)
                errors.append(f"{p.provider_name}: {str(e)}")

        err_details = "\n".join([f"- {e}" for e in errors]) or "- No provider is configured or permitted."
        return (
            f"All configured LLM providers failed to process the request:\n"
            f"{err_details}\n\n"
            f"Configure Gemini or a compatible API key and allow cloud context in Settings."
        )
