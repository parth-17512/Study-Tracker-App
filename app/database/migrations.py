import os
import shutil
from datetime import datetime
from sqlalchemy import text
from app.config.settings import DATA_DIR, logger

# We define the current schema version of the application code.
# V1 of the app is version 1. As we add columns for V2 features, we'll increment this.
CURRENT_SCHEMA_VERSION = 2

def backup_database():
    db_path = DATA_DIR / "studytrack.db"
    if not db_path.exists():
        return
        
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = backup_dir / f"studytrack_backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_file)
        logger.info(f"Database backed up successfully to {backup_file}")
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        raise

def get_current_version(engine):
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT version FROM db_version ORDER BY id DESC LIMIT 1")).fetchone()
            if result:
                return result[0]
            return 0
        except Exception:
            # Table probably doesn't exist
            return 0

def set_current_version(engine, version):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS db_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    migrated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("INSERT INTO db_version (version) VALUES (:version)"), {"version": version})

def run_migrations(engine):
    """
    Runs database migrations if necessary, ensuring a backup is taken first.
    """
    current_version = get_current_version(engine)
    logger.info(f"Current database version: {current_version}")
    
    if current_version == 0:
        # Check if tables exist to know if it's a fresh DB or an unversioned V1 DB
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='subjects'")).fetchone()
            if result:
                logger.info("Found unversioned V1 database. Setting initial version to 1.")
                set_current_version(engine, 1)
                current_version = 1
            else:
                logger.info("Fresh database detected. Initializing schema...")
                # We return False to indicate it's a fresh db, so create_all handles it, 
                # then we set version to CURRENT_SCHEMA_VERSION.
                return False
                
    if current_version < CURRENT_SCHEMA_VERSION:
        logger.info(f"Migrating database from version {current_version} to {CURRENT_SCHEMA_VERSION}...")
        backup_database()
        
        try:
            with engine.connect() as conn:
                with conn.begin():
                    if current_version < 2:
                        conn.execute(text("ALTER TABLE active_timer ADD COLUMN target_duration INTEGER"))
                        set_current_version(engine, 2)
                        current_version = 2
            
        except Exception as e:
            logger.critical(f"Database migration failed: {e}. Original data has been preserved in backup.")
            raise Exception(f"Migration failed: {e}")
            
    return True

def post_init_versioning(engine):
    """Called after Base.metadata.create_all to ensure fresh DBs get a version."""
    if get_current_version(engine) == 0:
        set_current_version(engine, CURRENT_SCHEMA_VERSION)
