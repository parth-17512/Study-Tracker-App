import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from app.ai.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    """Provider for hosted LLM services exposing the OpenAI chat-completions API."""

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
        provider_label: str = "Compatible API",
        timeout: int = 60,
    ):
        self.base_url = (base_url or "").strip().rstrip("/")
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip()
        self.provider_label = (provider_label or "Compatible API").strip()
        self.timeout = timeout

    @property
    def provider_id(self) -> str:
        return "openai_compatible"

    @property
    def provider_name(self) -> str:
        return f"{self.provider_label} ({self.model})"

    def is_available(self) -> Tuple[bool, str]:
        if not self.base_url:
            return False, "Compatible API base URL is not configured."
        if not self.api_key:
            return False, "Compatible API key is not configured."
        if not self.model:
            return False, "Compatible API model is not configured."
        if not self.base_url.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            return False, "Use HTTPS for remote compatible API endpoints."
        return True, f"{self.provider_label} is configured for model '{self.model}'."

    def _generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        available, reason = self.is_available()
        if not available:
            return f"ERROR: {reason}"

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "StudyTrack",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            choices = body.get("choices")
            if not isinstance(choices, list) or not choices:
                return "ERROR: Compatible API returned no completion choices."
            message = choices[0].get("message", {})
            content: Any = message.get("content", "") if isinstance(message, dict) else ""
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                )
            if not isinstance(content, str) or not content.strip():
                return "ERROR: Compatible API returned an empty response."
            return content.strip()
        except urllib.error.HTTPError as error:
            logger.warning("Compatible API request returned HTTP %s.", error.code)
            if error.code == 429:
                return "ERROR: [QUOTA_EXHAUSTED] Compatible API rate limit or quota reached (HTTP 429)."
            return f"ERROR: Compatible API request failed with HTTP {error.code}."
        except urllib.error.URLError as error:
            logger.warning("Compatible API request failed (%s).", type(error.reason).__name__)
            return "ERROR: Could not connect to the configured compatible API endpoint."
        except TimeoutError:
            logger.warning("Compatible API request timed out.")
            return f"ERROR: Compatible API request timed out after {self.timeout} seconds."
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, IndexError, TypeError) as error:
            logger.warning("Compatible API returned malformed data (%s).", type(error).__name__)
            return "ERROR: Compatible API returned a malformed response."
        except Exception as error:
            logger.warning("Compatible API request failed (%s).", type(error).__name__)
            return "ERROR: Compatible API request failed."

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self._generate(prompt, system_prompt)

    def generate_response(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        execute_tool_callback: callable,
    ) -> str:
        system_prompt = (
            "You are StudyTrack's AI Study Coach. Answer helpfully and accurately. "
            "Never invent facts, dates, or study hours."
        )
        return self._generate(prompt, system_prompt)
