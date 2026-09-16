import pytest
from datetime import datetime, timezone, timedelta
from app.services.session_service import SessionService
from app.database.models import StudySession

# We can reuse the db fixtures from test_timer_service or redefine them
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
    
    # 1. Create (Simulate TimerEngine completion)
    session1 = StudySession(start_time=now - timedelta(hours=1), end_time=now, duration_seconds=3600, topic="Math", session_type="stopwatch", status="COMPLETED")
    db_session.add(session1)
    db_session.commit()
    
    session_id = session1.id
    
    # 2. Read
    fetched = service.get_session(session_id)
    assert fetched is not None
    assert fetched.topic == "Math"
    
    all_sessions = service.get_all_sessions()
    assert len(all_sessions) > 0
    
    # 3. Update
    service.update_session(session_id, {"notes": "Hard chapter", "duration_seconds": 4000})
    db_session.expire_all() # force refresh
    
    updated = service.get_session(session_id)
    assert updated.notes == "Hard chapter"
    assert updated.duration_seconds == 4000
    
    # Validation constraint
    with pytest.raises(ValueError):
        service.update_session(session_id, {"duration_seconds": -10})
        
    # 4. Delete
    result = service.delete_session(session_id)
    assert result is True
    assert service.get_session(session_id) is None
