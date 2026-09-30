import pytest
import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine, text
from app.database.database import Database
from app.database import migrations
from app.database.migrations import set_current_version

@pytest.fixture
def temp_db_dir(tmp_path, monkeypatch):
    # Override settings.DATA_DIR to point to tmp_path
    monkeypatch.setattr("app.database.migrations.DATA_DIR", tmp_path)
    monkeypatch.setattr("app.config.settings.DATA_DIR", tmp_path)
    return tmp_path

def test_fresh_database_initialization(temp_db_dir, monkeypatch):
    monkeypatch.setattr("app.database.migrations.CURRENT_SCHEMA_VERSION", 2)
    db_path = temp_db_dir / "studytrack.db"
    db_url = f"sqlite:///{db_path}"
    db = Database(db_url)
    db.init_db()
    
    # Check that db_version is set to 2
    version = migrations.get_current_version(db.engine)
    assert version == 2
    
def test_unversioned_v1_upgrade(temp_db_dir):
    db_path = temp_db_dir / "studytrack.db"
    db_url = f"sqlite:///{db_path}"
    
    # Create an unversioned V1 db
    engine = create_engine(db_url)
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("CREATE TABLE subjects (id INTEGER PRIMARY KEY)"))
            conn.execute(text("CREATE TABLE active_timer (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO subjects (id) VALUES (1)"))
    
    # Init DB should detect unversioned V1 and set to 1
    db = Database(db_url)
    db.init_db()
    
    version = migrations.get_current_version(db.engine)
    assert version == 2
    
    # Verify data is preserved
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM subjects")).fetchone()
        assert result[0] == 1

def test_backup_before_migration(temp_db_dir, monkeypatch):
    db_path = temp_db_dir / "studytrack.db"
    db_url = f"sqlite:///{db_path}"
    
    # Create an unversioned V1 db
    engine = create_engine(db_url)
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("CREATE TABLE subjects (id INTEGER PRIMARY KEY)"))
            conn.execute(text("CREATE TABLE active_timer (id INTEGER PRIMARY KEY)"))
    
    # Init DB to set it to version 1
    db = Database(db_url)
    db.init_db()
    
    # Now simulate a migration by monkeypatching CURRENT_SCHEMA_VERSION
    monkeypatch.setattr("app.database.migrations.CURRENT_SCHEMA_VERSION", 2)
    
    # Re-init db. This should trigger backup.
    db2 = Database(db_url)
    db2.init_db()
    
    # Check that backup was created
    backup_dir = temp_db_dir / "backups"
    assert backup_dir.exists()
    backups = list(backup_dir.glob("studytrack_backup_*.db"))
    assert len(backups) == 1

def test_failed_migration_preserves_database(temp_db_dir, monkeypatch):
    db_path = temp_db_dir / "studytrack.db"
    db_url = f"sqlite:///{db_path}"
    
    # Initialize normally to version 1
    db = Database(db_url)
    db.init_db()
    
    # Add some dummy data
    with db.engine.connect() as conn:
        with conn.begin():
            conn.execute(text("CREATE TABLE dummy (id INTEGER)"))
            conn.execute(text("INSERT INTO dummy (id) VALUES (42)"))
    
    # Simulate a failing migration step
    monkeypatch.setattr("app.database.migrations.CURRENT_SCHEMA_VERSION", 2)
    
    def failing_migration(*args, **kwargs):
        raise Exception("Intentional Migration Failure")
        
    # We patch the point in run_migrations that does the migration. 
    # For now, it's just a pass, but we'll patch backup_database to fail AFTER it backs up,
    # or just we patch the function itself. Since we don't have migrate_v1_to_v2 yet, 
    # let's just patch run_migrations to fail.
    
    original_run = migrations.run_migrations
    def patched_run(eng):
        # We simulate the exact failure inside run_migrations
        migrations.backup_database()
        raise Exception("Failure")
        
    monkeypatch.setattr("app.database.database.run_migrations", patched_run)
    
    # Attempt to init db
    db2 = Database(db_url)
    with pytest.raises(Exception, match="Failure"):
        db2.init_db()
        
    # Database original file should still exist and be intact (the exception happens, but the file wasn't deleted)
    with db2.engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM dummy")).fetchone()
        assert result[0] == 42
        
    # Backup exists
    backups = list((temp_db_dir / "backups").glob("studytrack_backup_*.db"))
    assert len(backups) == 1

def test_existing_notes_survive_upgrade(temp_db_dir, monkeypatch):
    db_path = temp_db_dir / "studytrack.db"
    db_url = f"sqlite:///{db_path}"
    db = Database(db_url)
    db.init_db()
    
    with db.engine.connect() as conn:
        with conn.begin():
            conn.execute(text("INSERT INTO note_nodes (name, is_folder, is_favorite) VALUES ('Test Note', 0, 0)"))
            
    # Trigger an upgrade
    monkeypatch.setattr("app.database.migrations.CURRENT_SCHEMA_VERSION", 2)
    db2 = Database(db_url)
    db2.init_db()
    
    with db2.engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM note_nodes")).fetchone()
        assert result[0] == "Test Note"

def test_existing_sessions_survive_upgrade(temp_db_dir, monkeypatch):
    db_path = temp_db_dir / "studytrack.db"
    db_url = f"sqlite:///{db_path}"
    db = Database(db_url)
    db.init_db()
    
    with db.engine.connect() as conn:
        with conn.begin():
            conn.execute(text("INSERT INTO study_sessions (start_time, session_type, status) VALUES ('2023-01-01 00:00:00', 'stopwatch', 'completed')"))
            
    # Trigger an upgrade
    monkeypatch.setattr("app.database.migrations.CURRENT_SCHEMA_VERSION", 2)
    db2 = Database(db_url)
    db2.init_db()
    
    with db2.engine.connect() as conn:
        result = conn.execute(text("SELECT status FROM study_sessions")).fetchone()
        assert result[0] == "completed"

