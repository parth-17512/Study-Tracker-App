import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import DATABASE_URL, logger

Base = declarative_base()

class Database:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}, # Required for SQLite
            echo=False # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """Creates all tables in the database."""
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=self.engine)
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
