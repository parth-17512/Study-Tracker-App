import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import ActiveTimer
from app.services.timer_service import TimerService

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

# Mock the database class to return our test session
class MockDB:
    def __init__(self, session):
        self.session = session
    
    from contextlib import contextmanager
    @contextmanager
    def get_session(self):
        yield self.session
        self.session.commit()

def test_timer_service_persistence(db_session):
    db = MockDB(db_session)
    service = TimerService(db=db)
    
    # Start timer, it should persist to DB
    service.start_stopwatch(topic="Math")
    
    active_timer = db_session.query(ActiveTimer).first()
    assert active_timer is not None
    assert active_timer.state == "RUNNING"
    assert active_timer.topic == "Math"
    
    # Pause it
    service.pause()
    active_timer = db_session.query(ActiveTimer).first()
    assert active_timer.state == "PAUSED"
    
    # Cancel it (clears the table)
    service.cancel()
    active_timer = db_session.query(ActiveTimer).first()
    assert active_timer is None

def test_timer_service_startup_recovery(db_session):
    db = MockDB(db_session)
    service = TimerService(db=db)
    
    service.start_countdown(duration_seconds=3600, topic="Physics")
    
    # Simulate app restart by creating a new service instance
    new_service = TimerService(db=db)
    found = new_service.check_active_timer()
    
    assert found is True
    assert new_service.engine.state.value == "RUNNING"
    assert new_service.engine.topic == "Physics"
    
    # Clean up
    new_service.cancel()
