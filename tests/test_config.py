import os
import json
import pytest
from app.config.config_manager import ConfigManager
from app.config.settings import DATA_DIR

@pytest.fixture
def config_manager():
    # Force re-initialization for tests
    ConfigManager._instance = None
    manager = ConfigManager()
    
    # Store backup of original if it exists
    original_path = manager.config_file
    test_path = DATA_DIR / "test_settings.json"
    manager.config_file = test_path
    
    yield manager
    
    # Cleanup
    if test_path.exists():
        os.remove(test_path)
    ConfigManager._instance = None

def test_default_settings(config_manager):
    assert config_manager.get("sound_enabled") is True
    assert config_manager.get("notifications_enabled") is True
    assert config_manager.get("theme") == "dark"

def test_save_and_load(config_manager):
    config_manager.set("sound_enabled", False)
    config_manager.set("theme", "light")
    
    # Verify in memory
    assert config_manager.get("sound_enabled") is False
    
    # Force reload from disk
    config_manager.load()
    assert config_manager.get("sound_enabled") is False
    assert config_manager.get("theme") == "light"
