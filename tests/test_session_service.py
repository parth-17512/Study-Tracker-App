import pytest
from datetime import datetime, timezone, timedelta
from app.services.session_service import SessionService
from app.database.models import StudySession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base

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

class MockDB:
    def __init__(self, session):
        self.session = session
    from contextlib import contextmanager
    @contextmanager
    def get_session(self):
        yield self.session
        self.session.commit()

def test_session_crud(db_session):
    db = MockDB(db_session)
    service = SessionService(db=db)
    
    now = datetime.now(timezone.utc)
    
    session1 = StudySession(start_time=now - timedelta(hours=1), end_time=now, duration_seconds=3600, topic="Math", session_type="stopwatch", status="COMPLETED")
    db_session.add(session1)
    db_session.commit()
    
    session_id = session1.id
    
    fetched = service.get_session(session_id)
    assert fetched is not None
    assert fetched.topic == "Math"
    
    all_sessions = service.get_all_sessions()
    assert len(all_sessions) > 0
    
    service.update_session(session_id, {"notes": "Hard chapter", "duration_seconds": 4000})
    db_session.expire_all()
    
    updated = service.get_session(session_id)
    assert updated.notes == "Hard chapter"
    assert updated.duration_seconds == 4000
    
    with pytest.raises(ValueError):
        service.update_session(session_id, {"duration_seconds": -10})
        
    result = service.delete_session(session_id)
    assert result is True
    assert service.get_session(session_id) is None

def test_update_session_name_preserves_metadata(db_session):
    db = MockDB(db_session)
    service = SessionService(db=db)

    start_time = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 10, 20, 11, 30, tzinfo=timezone.utc)
    duration = 5400
    notes = "Chapter 4 exercises"

    session = StudySession(
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration,
        topic="Math",
        notes=notes,
        session_type="stopwatch",
        status="COMPLETED"
    )
    db_session.add(session)
    db_session.commit()

    # Update topic name
    success = service.update_session_name(session.id, "Advanced Linear Algebra")
    assert success is True

    db_session.expire_all()
    refreshed = service.get_session(session.id)

    # Verify name updated
    assert refreshed.topic == "Advanced Linear Algebra"
    # Verify other metadata preserved
    assert refreshed.start_time == start_time.replace(tzinfo=None)
    assert refreshed.end_time == end_time.replace(tzinfo=None)
    assert refreshed.duration_seconds == duration
    assert refreshed.notes == notes
    assert refreshed.status == "COMPLETED"

def test_update_session_name_validation(db_session):
    db = MockDB(db_session)
    service = SessionService(db=db)

    now = datetime.now(timezone.utc)
    session = StudySession(start_time=now, duration_seconds=1800, topic="Physics", session_type="stopwatch", status="COMPLETED")
    db_session.add(session)
    db_session.commit()

    # Reject empty name
    with pytest.raises(ValueError, match="cannot be empty"):
        service.update_session_name(session.id, "")

    # Reject whitespace only
    with pytest.raises(ValueError, match="cannot be empty"):
        service.update_session_name(session.id, "   ")

    # Trim accidental surrounding whitespace
    service.update_session_name(session.id, "   Quantum Mechanics   ")
    db_session.expire_all()
    refreshed = service.get_session(session.id)
    assert refreshed.topic == "Quantum Mechanics"
