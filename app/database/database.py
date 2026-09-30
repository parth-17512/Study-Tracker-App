import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import DATABASE_URL, logger

from app.database.migrations import run_migrations, post_init_versioning

Base = declarative_base()

class Database:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}, # Required for SQLite
            echo=False # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine, 
            expire_on_commit=False
        )
    
    def init_db(self):
        """Creates all tables in the database."""
        logger.info("Initializing database schema...")
        
        # Ensure all models are imported and registered with Base
        import app.database.models
        
        # Run migrations before SQLAlchemy's create_all to allow schema evolution
        is_existing_db = run_migrations(self.engine)
        
        Base.metadata.create_all(bind=self.engine)
        
        # Mark fresh DBs with the current version
        if not is_existing_db:
            post_init_versioning(self.engine)
            
        logger.info("Database schema initialized.")

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            session.close()

# Global database instance
db = Database()
