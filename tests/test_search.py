import pytest
from datetime import datetime, timezone, timedelta
from app.repositories.session_repository import SessionRepository
from app.database.models import StudySession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    # Add dummy data
    now = datetime.now(timezone.utc)
    
    s1 = StudySession(
        topic="Math",
        notes="Calculus homework",
        status="COMPLETED",
        session_type="POMODORO",
        start_time=now,
        duration_seconds=3600
    )
    s2 = StudySession(
        topic="Physics",
        notes="Quantum mechanics is hard",
        status="COMPLETED",
        session_type="FLOW",
        start_time=now - timedelta(days=1),
        duration_seconds=7200
    )
    s3 = StudySession(
        topic="Math",
        notes="More calc",
        status="CANCELLED",
        session_type="POMODORO",
        start_time=now - timedelta(days=2),
        duration_seconds=600
    )
    
    db_session.add_all([s1, s2, s3])
    db_session.commit()
    
    yield db_session
    db_session.close()

def test_search_by_text(session):
    repo = SessionRepository()
    
    # Search by topic
    results = repo.search_sessions(session, text_query="Math")
    assert len(results) == 2
    
    # Search by notes
    results = repo.search_sessions(session, text_query="quantum")
    assert len(results) == 1
    assert results[0].topic == "Physics"
    
def test_search_by_topic_and_status(session):
    repo = SessionRepository()
    
    # Exact topic match
    results = repo.search_sessions(session, topic="Math")
    assert len(results) == 2
    
    # Exact status match
    results = repo.search_sessions(session, status="CANCELLED")
    assert len(results) == 1
    assert results[0].status == "CANCELLED"
    
    # Topic AND status match
    results = repo.search_sessions(session, topic="Math", status="COMPLETED")
    assert len(results) == 1
    assert results[0].notes == "Calculus homework"

def test_search_ordering(session):
    repo = SessionRepository()
    
    # Newest (s1, s2, s3)
    results = repo.search_sessions(session, order_by="newest")
    assert results[0].topic == "Math"
    assert results[0].duration_seconds == 3600
    
    # Oldest (s3, s2, s1)
    results = repo.search_sessions(session, order_by="oldest")
    assert results[0].duration_seconds == 600
    
    # Longest (s2, s1, s3)
    results = repo.search_sessions(session, order_by="longest")
    assert results[0].duration_seconds == 7200
    
    # Shortest (s3, s1, s2)
    results = repo.search_sessions(session, order_by="shortest")
    assert results[0].duration_seconds == 600
