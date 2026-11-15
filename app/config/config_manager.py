import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from app.config.settings import DATA_DIR

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages persistent application settings using a JSON file."""

    DAILY_GOAL_CHANGE_INTERVAL = timedelta(days=7)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
        
    def _init(self):
        self.config_file = DATA_DIR / "settings.json"
        
        # Default settings
        self.default_settings = {
            "sound_enabled": True,
            "desktop_notifications": True,
            "theme": "dark",
            "default_pomodoro_minutes": 25,
            "daily_goal_seconds": 6 * 3600,
            "gemini_api_key": "",
            "llm_provider_priority": "gemini_first",
            "compatible_api_base_url": "",
            "compatible_api_key": "",
            "compatible_api_model": "",
            "compatible_api_label": "Compatible API",
            "compatible_api_timeout": 60,
            "cloud_consent": False,
            "cloud_consent_configured": False
        }
        self.settings = self.default_settings.copy()
        
        self.load()

    def load(self):
        """Loads settings from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
                    legacy_priorities = {
                        "ollama_first", "ollama_cloud_first", "ollama_only",
                        "gemini_cloud_first",
                    }
                    if loaded.get("llm_provider_priority") in legacy_priorities:
                        self.settings["llm_provider_priority"] = "gemini_first"
                    if not loaded.get("cloud_consent_configured", False):
                        # Older settings may contain the former permissive default; require an explicit opt-in.
                        self.settings["cloud_consent"] = False
                    logger.info("Settings loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        else:
            self.save() # Create with defaults
            
    def save(self):
        """Saves settings to disk."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
                logger.info("Settings saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def get_daily_goal_change_available_at(self):
        """Return the next allowed goal-change time in UTC, if a change was saved."""
        last_changed_at = self.get("daily_goal_last_changed_at")
        if not last_changed_at:
            return None

        try:
            changed_at = datetime.fromisoformat(last_changed_at)
        except (TypeError, ValueError):
            logger.warning("Invalid daily goal change timestamp; allowing a new goal change.")
            return None

        if changed_at.tzinfo is None:
            changed_at = changed_at.replace(tzinfo=timezone.utc)
        else:
            changed_at = changed_at.astimezone(timezone.utc)

        return changed_at + self.DAILY_GOAL_CHANGE_INTERVAL

    def can_change_daily_goal(self, now=None):
        """Return whether the seven-day daily-goal change interval has elapsed."""
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)

        available_at = self.get_daily_goal_change_available_at()
        return available_at is None or now >= available_at

    def update_daily_goal(self, seconds: int, now=None) -> bool:
        """Persist a daily-goal change and start its seven-day cooldown."""
        if seconds <= 0:
            raise ValueError("Daily goal must be greater than zero.")
        if seconds == self.get("daily_goal_seconds", 6 * 3600):
            return True
        if not self.can_change_daily_goal(now):
            return False

        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)

        previous_goal = self.get("daily_goal_seconds", 6 * 3600)
        previous_changed_at = self.get("daily_goal_last_changed_at")
        self.settings["daily_goal_seconds"] = seconds
        self.settings["daily_goal_last_changed_at"] = now.isoformat()

        if self.save():
            return True

        self.settings["daily_goal_seconds"] = previous_goal
        if previous_changed_at is None:
            self.settings.pop("daily_goal_last_changed_at", None)
        else:
            self.settings["daily_goal_last_changed_at"] = previous_changed_at
        return False
            
    def get(self, key: str, default=None):
        return self.settings.get(key, default)
        
    def set(self, key: str, value):
        self.settings[key] = value
        self.save()
