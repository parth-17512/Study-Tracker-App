import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import Subject, Goal

# In-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    return create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_subject(db_session):
    subject = Subject(name="Test Subject", description="A test subject")
    db_session.add(subject)
    db_session.commit()
    
    assert subject.id is not None
    assert subject.name == "Test Subject"
    assert subject.is_active is True

def test_create_goal(db_session):
    goal = Goal(goal_type="daily", target_seconds=3600)
    db_session.add(goal)
    db_session.commit()
    
    assert goal.id is not None
    assert goal.target_seconds == 3600
    assert goal.goal_type == "daily"
