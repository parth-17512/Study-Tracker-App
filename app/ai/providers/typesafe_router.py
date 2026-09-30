import os
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Only import TypeSafe if we have typesafe installed, otherwise we mock it for development without key
try:
    from typesafe import TypeSafe
    HAS_TYPESAFE = True
except ImportError:
    HAS_TYPESAFE = False

class UserIntent(BaseModel):
    action: Literal["search_notes", "get_stats", "general_chat"] = Field(
        description="The action the user wants to perform."
    )
    search_query: Optional[str] = Field(
        description="If action is search_notes, the distilled query to search for. Otherwise null.",
        default=None
    )

class TypeSafeRouter:
    def __init__(self):
        from app.config.config_manager import ConfigManager
        config = ConfigManager()
        self.api_key = config.get("typesafe_api_key", "").strip() or os.getenv("TYPESAFE_API_KEY", "")
        
        if HAS_TYPESAFE and self.api_key:
            # Point to BeatAPI for the free tier model
            self.client = TypeSafe(api_key=self.api_key, base_url="https://api.beatapi.io/v1")
        else:
            self.client = None
            
    def classify_intent(self, user_prompt: str) -> UserIntent:
        if self.client:
            try:
                # Use free Jev model for instantaneous structured classification
                result = self.client.classify(
                    prompt=user_prompt,
                    response_model=UserIntent,
                    model="jev-1.13-free"
                )
                return result
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"TypeSafe classification failed: {e}")
                
        # Fallback heuristic if no API key or if it fails
        lower_prompt = user_prompt.lower()
        if any(w in lower_prompt for w in ["note", "search", "find", "where", "summarize", "explain"]):
            return UserIntent(action="search_notes", search_query=user_prompt)
        elif any(w in lower_prompt for w in ["stat", "duration", "streak", "time", "how long"]):
            return UserIntent(action="get_stats", search_query=None)
            
        return UserIntent(action="general_chat", search_query=None)

intent_router = TypeSafeRouter()
