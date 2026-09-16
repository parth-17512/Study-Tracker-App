import pytest
from datetime import datetime, timezone, timedelta
from app.services.analytics_service import AnalyticsService
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

def test_daily_total(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    
    now = datetime.now(timezone.utc)
    
    # Create a session for today
    session1 = StudySession(start_time=now - timedelta(hours=1), end_time=now, duration_seconds=3600, status="COMPLETED", session_type="stopwatch")
    db_session.add(session1)
    
    # Create a session for yesterday
    yesterday = now - timedelta(days=1)
    session2 = StudySession(start_time=yesterday - timedelta(hours=1), end_time=yesterday, duration_seconds=1800, status="COMPLETED", session_type="stopwatch")
    db_session.add(session2)
    
    db_session.commit()
    
    # Calculate daily total for today
    today_total = service.get_daily_total_seconds(now)
    assert today_total == 3600
    
    # Calculate daily total for yesterday
    yesterday_total = service.get_daily_total_seconds(yesterday)
    assert yesterday_total == 1800

def test_streak_calculation(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    
    now = datetime.now(timezone.utc)
    
    # Calculate streak, should be 2 (yesterday + today) based on previous test data
    streak = service.calculate_current_streak(now)
    assert streak == 2
    
    # If "today" is tomorrow, the streak is still 2 because they studied yesterday (which is "today" relative to the DB)
    # Actually wait: 
    # If we pass `now + timedelta(days=1)` (meaning tomorrow), 
    # DB has [today, yesterday].
    # Current date: tomorrow. Did they study tomorrow? No.
    # Did they study "today"? Yes. So streak is maintained and counts today + yesterday = 2.
    tomorrow = now + timedelta(days=1)
    streak_tomorrow = service.calculate_current_streak(tomorrow)
    assert streak_tomorrow == 2
    
    # If "today" is the day after tomorrow, streak should break
    day_after_tomorrow = now + timedelta(days=2)
    streak_broken = service.calculate_current_streak(day_after_tomorrow)
    assert streak_broken == 0

def test_recent_sessions(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    
    recent = service.get_recent_sessions(limit=1)
    assert len(recent) == 1
    # Order is descending by start_time, so the most recent is the one from today
    assert recent[0].duration_seconds == 3600

def test_yearly_heatmap_data(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    
    now = datetime.now(timezone.utc)
    current_year = now.year
    
    data = service.get_yearly_heatmap_data(current_year)
    
    # Based on the earlier test data in `test_daily_total`, there is a session today and yesterday
    today_date = now.date()
    yesterday_date = (now - timedelta(days=1)).date()
    
    assert today_date in data
    assert data[today_date] == 3600
    
    assert yesterday_date in data
    assert data[yesterday_date] == 1800
    
    # Future dates should not be in there
    tomorrow = (now + timedelta(days=1)).date()
    assert data.get(tomorrow, 0) == 0

def test_monthly_study_data(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    
    now = datetime.now(timezone.utc)
    
    data = service.get_monthly_study_data(now.year, now.month)
    
    today_date = now.date()
    yesterday_date = (now - timedelta(days=1)).date()
    
    # We should have the data from test_daily_total
    # (Assuming both today and yesterday are in the same month for this test, 
    # which is true most days except the 1st of the month. 
    # For a robust test, we would normally inject specific dates, but this works given our mock data).
    if today_date.month == yesterday_date.month:
        assert today_date in data
        assert data[today_date] == 3600
        assert yesterday_date in data
        assert data[yesterday_date] == 1800
    
    # Next month should be empty
    next_month = now.month + 1 if now.month < 12 else 1
    next_year = now.year if now.month < 12 else now.year + 1
    empty_data = service.get_monthly_study_data(next_year, next_month)
    assert len(empty_data) == 0
