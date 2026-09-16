import json
import logging
from pathlib import Path
from app.config.settings import DATA_DIR

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages persistent application settings using a JSON file."""
    
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
            "gemini_api_key": ""
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
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            
    def get(self, key: str, default=None):
        return self.settings.get(key, default)
        
    def set(self, key: str, value):
        self.settings[key] = value
        self.save()
