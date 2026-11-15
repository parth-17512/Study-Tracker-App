import os
import json
import pytest
from app.config.config_manager import ConfigManager
from app.config.settings import DATA_DIR
from datetime import datetime, timedelta, timezone

@pytest.fixture
def config_manager():
    # Force re-initialization for tests
    ConfigManager._instance = None
    manager = ConfigManager()
    
    # Store backup of original if it exists
    original_path = manager.config_file
    manager.settings = manager.default_settings.copy()
    test_path = DATA_DIR / "test_settings.json"
    manager.config_file = test_path
    
    yield manager
    
    # Cleanup
    if test_path.exists():
        os.remove(test_path)
    ConfigManager._instance = None

def test_default_settings(config_manager):
    assert config_manager.get("sound_enabled") is True
    assert config_manager.get("desktop_notifications") is True
    assert config_manager.get("theme") == "dark"
    assert config_manager.get("cloud_consent") is False
    assert config_manager.get("daily_goal_seconds") == 6 * 3600

def test_save_and_load(config_manager):
    config_manager.set("sound_enabled", False)
    config_manager.set("theme", "light")
    
    # Verify in memory
    assert config_manager.get("sound_enabled") is False
    
    # Force reload from disk
    config_manager.load()
    assert config_manager.get("sound_enabled") is False
    assert config_manager.get("theme") == "light"

def test_corrupt_json_recovery(config_manager):
    # Write garbage to the file
    with open(config_manager.config_file, 'w', encoding='utf-8') as f:
        f.write("{ invalid_json: true, ]")
        
    # Force reload
    config_manager.load()
    
    # Should not crash, and should fall back to defaults (or whatever was in memory)
    assert config_manager.get("sound_enabled") is not None

def test_legacy_cloud_consent_requires_explicit_opt_in(config_manager):
    with open(config_manager.config_file, "w", encoding="utf-8") as config_file:
        json.dump({"cloud_consent": True}, config_file)

    config_manager.load()

    assert config_manager.get("cloud_consent") is False
    assert config_manager.get("cloud_consent_configured") is False


def test_migrating_legacy_provider_priority_keeps_cloud_consent_opt_in(config_manager):
    with open(config_manager.config_file, "w", encoding="utf-8") as config_file:
        json.dump({
            "llm_provider_priority": "ollama_first",
            "gemini_api_key": "configured-key",
        }, config_file)

    config_manager.load()

    assert config_manager.get("llm_provider_priority") == "gemini_first"
    assert config_manager.get("cloud_consent") is False


def test_daily_goal_can_only_change_once_per_rolling_week(config_manager):
    now = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)

    assert config_manager.update_daily_goal(8 * 3600, now=now) is True
    config_manager.load()
    assert config_manager.get("daily_goal_seconds") == 8 * 3600
    assert config_manager.can_change_daily_goal(now=now + timedelta(days=6, hours=23)) is False
    assert config_manager.update_daily_goal(7 * 3600, now=now + timedelta(days=6, hours=23)) is False
    assert config_manager.get("daily_goal_seconds") == 8 * 3600

    available_at = now + timedelta(days=7)
    assert config_manager.get_daily_goal_change_available_at() == available_at
    assert config_manager.update_daily_goal(7 * 3600, now=available_at) is True
    assert config_manager.get("daily_goal_seconds") == 7 * 3600


def test_unchanged_daily_goal_does_not_start_cooldown(config_manager):
    now = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)

    assert config_manager.update_daily_goal(6 * 3600, now=now) is True
    assert config_manager.get_daily_goal_change_available_at() is None
    assert config_manager.update_daily_goal(7 * 3600, now=now) is True
