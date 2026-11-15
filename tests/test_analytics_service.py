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
        session.query(StudySession).delete()
        session.commit()
        yield session
    finally:
        session.query(StudySession).delete()
        session.commit()
        session.close()

class MockDB:
    def __init__(self, session):
        self.session = session
    from contextlib import contextmanager
    @contextmanager
    def get_session(self):
        yield self.session
        self.session.commit()


def seed_standard_sessions(db_session, now):
    today = now
    yesterday = now - timedelta(days=1)
    session1 = StudySession(
        start_time=today - timedelta(hours=1),
        end_time=today,
        duration_seconds=3600,
        status="COMPLETED",
        session_type="stopwatch",
    )
    session2 = StudySession(
        start_time=yesterday - timedelta(hours=1),
        end_time=yesterday,
        duration_seconds=1800,
        status="COMPLETED",
        session_type="stopwatch",
    )
    db_session.add_all([session1, session2])
    db_session.commit()
    return session1, session2


def test_daily_total(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    now = datetime.now(timezone.utc)
    seed_standard_sessions(db_session, now)

    today_total = service.get_daily_total_seconds(now)
    assert today_total == 3600

    yesterday = now - timedelta(days=1)
    yesterday_total = service.get_daily_total_seconds(yesterday)
    assert yesterday_total == 1800


def test_streak_calculation(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)

    now = datetime.now(timezone.utc)
    db_session.add_all([
        StudySession(
            start_time=now - timedelta(hours=1),
            end_time=now,
            duration_seconds=3 * 3600,
            status="COMPLETED",
            session_type="stopwatch",
        ),
        StudySession(
            start_time=now - timedelta(days=1) - timedelta(hours=1),
            end_time=now - timedelta(days=1),
            duration_seconds=3 * 3600 + 1800,
            status="COMPLETED",
            session_type="stopwatch",
        ),
    ])
    db_session.commit()

    streak = service.calculate_current_streak(now)
    assert streak == 2

    tomorrow = now + timedelta(days=1)
    streak_tomorrow = service.calculate_current_streak(tomorrow)
    assert streak_tomorrow == 2

    day_after_tomorrow = now + timedelta(days=2)
    streak_broken = service.calculate_current_streak(day_after_tomorrow)
    assert streak_broken == 0


def test_recent_sessions(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    now = datetime.now(timezone.utc)
    seed_standard_sessions(db_session, now)

    recent = service.get_recent_sessions(limit=1)
    assert len(recent) == 1
    assert recent[0].duration_seconds == 3600


def test_yearly_heatmap_data(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    now = datetime.now(timezone.utc)
    seed_standard_sessions(db_session, now)
    current_year = now.year

    data = service.get_yearly_heatmap_data(current_year)

    today_date = now.date()
    yesterday_date = (now - timedelta(days=1)).date()

    assert today_date in data
    assert data[today_date] == 3600

    assert yesterday_date in data
    assert data[yesterday_date] == 1800

    tomorrow = (now + timedelta(days=1)).date()
    assert data.get(tomorrow, 0) == 0


def test_monthly_study_data(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    now = datetime.now(timezone.utc)
    seed_standard_sessions(db_session, now)

    data = service.get_monthly_study_data(now.year, now.month)

    today_date = now.date()
    yesterday_date = (now - timedelta(days=1)).date()

    if today_date.month == yesterday_date.month:
        assert today_date in data
        assert data[today_date] == 3600
        assert yesterday_date in data
        assert data[yesterday_date] == 1800

    next_month = now.month + 1 if now.month < 12 else 1
    next_year = now.year if now.month < 12 else now.year + 1
    empty_data = service.get_monthly_study_data(next_year, next_month)
    assert len(empty_data) == 0


def test_advanced_analytics(db_session):
    db = MockDB(db_session)
    service = AnalyticsService(db=db)
    now = datetime.now(timezone.utc)
    seed_standard_sessions(db_session, now)

    stats = service.get_summary_stats()
    assert stats["total_sessions"] == 2
    assert stats["total_seconds"] == 5400
    assert stats["avg_session_seconds"] == 2700

    comps = service.get_period_comparisons(now)
    assert (comps["this_week"] + comps["last_week"]) == 5400

    dist = service.get_topic_distribution()
    assert "Uncategorized" in dist
    assert dist["Uncategorized"] == 5400

    last_7 = service.get_last_7_days_chart_data(now)
    assert len(last_7) == 7
    assert last_7[now.date()] == 3600
    assert last_7[(now - timedelta(days=1)).date()] == 1800
