import pytest
from datetime import datetime, date, timedelta, timezone, tzinfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, Database
from app.database.models import StudySession, NoteNode
from app.services.analytics_service import AnalyticsService
from app.services.note_service import NoteService
from app.services.coach_service import CoachService
from app.ai.agent import StudyCoachAgent
from app.ai.providers.base import LLMProvider

class CustomTestTZ(tzinfo):
    """Custom UTC+5:30 fixed offset timezone for testing boundary interpretation."""
    def utcoffset(self, dt):
        return timedelta(hours=5, minutes=30)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "+05:30"

class FailingLLMProvider(LLMProvider):
    """Simulates a provider that throws an error or quota exhaustion."""
    def generate_response(self, prompt, tools_schema, execute_tool_callback):
        raise RuntimeError("429 Resource Exhausted: Quota exceeded")

class EmptyLLMProvider(LLMProvider):
    """Simulates a provider returning an empty string."""
    def generate_response(self, prompt, tools_schema, execute_tool_callback):
        return ""

class MockEchoProvider(LLMProvider):
    """Simple mock provider that echoes facts back."""
    def generate_response(self, prompt, tools_schema, execute_tool_callback):
        return f"[AI COACH RESPONSE]\nBased on your records:\n{prompt}"

class InMemoryDatabase(Database):
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

@pytest.fixture
def test_setup():
    db = InMemoryDatabase()
    test_tz = CustomTestTZ()
    analytics = AnalyticsService(db=db)
    notes = NoteService(db_override=db)

    agent = StudyCoachAgent(provider=MockEchoProvider())
    coach = CoachService(agent=agent, analytics_service=analytics, note_service=notes, tz=test_tz)

    return {
        "db": db,
        "analytics": analytics,
        "notes": notes,
        "agent": agent,
        "coach": coach,
        "tz": test_tz
    }

# 1. Retrieve notes created today
def test_retrieve_notes_created_today(test_setup):
    notes_service = test_setup["notes"]
    coach = test_setup["coach"]

    folder = notes_service.create_node("Computer Science", is_folder=True)
    note = notes_service.create_node("Algorithms Notes", is_folder=False, parent_id=folder.id)
    notes_service.update_node_content(note.id, "Learned Dijkstra and A* search today.")

    response = coach.process_query("What notes did I write today?")
    assert "Algorithms Notes" in response
    assert "Dijkstra" in response or "Computer Science" in response


def test_search_and_recent_coach_notes_include_parent_folder_when_detached(test_setup):
    notes_service = test_setup["notes"]
    coach = test_setup["coach"]

    folder = notes_service.create_node("Computer Science", is_folder=True)
    note = notes_service.create_node(
        "Algorithms Notes", is_folder=False, parent_id=folder.id
    )
    notes_service.update_node_content(note.id, "Dijkstra graph traversal")

    search_response = coach.process_query("Search notes for Dijkstra")
    recent_response = coach.process_query("Show my recent notes")

    assert "Computer Science" in search_response
    assert "Computer Science" in recent_response

# 2. Retrieve notes from a specified past date
def test_retrieve_notes_from_specified_past_date(test_setup):
    db = test_setup["db"]
    coach = test_setup["coach"]
    past_date_str = "2026-10-15"
    past_dt = datetime(2026, 10, 15, 14, 30, tzinfo=timezone.utc)

    with db.get_session() as session:
        note = NoteNode(
            name="Ancient History Notes",
            is_folder=False,
            content="Roman Empire architecture and roads.",
            created_at=past_dt,
            updated_at=past_dt
        )
        session.add(note)
        session.commit()

    response = coach.process_query(f"What notes did I write on {past_date_str}?")
    assert "Ancient History Notes" in response
    assert "Roman Empire" in response

# 3. Retrieve notes across a date range
def test_retrieve_notes_across_date_range(test_setup):
    db = test_setup["db"]
    notes_service = test_setup["notes"]

    d1 = datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc)
    d2 = datetime(2026, 10, 12, 10, 0, tzinfo=timezone.utc)
    d3 = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)

    with db.get_session() as session:
        n1 = NoteNode(name="Note 10th", is_folder=False, content="Day 10", created_at=d1, updated_at=d1)
        n2 = NoteNode(name="Note 12th", is_folder=False, content="Day 12", created_at=d2, updated_at=d2)
        n3 = NoteNode(name="Note 20th", is_folder=False, content="Day 20", created_at=d3, updated_at=d3)
        session.add_all([n1, n2, n3])
        session.commit()

    range_notes = notes_service.get_notes_by_date_range("2026-10-09", "2026-10-15")
    names = [n["name"] for n in range_notes]
    assert "Note 10th" in names
    assert "Note 12th" in names
    assert "Note 20th" not in names

def test_coach_answers_notes_across_explicit_date_range(test_setup):
    db = test_setup["db"]
    coach = test_setup["coach"]
    dates = [
        datetime(2026, 10, 10, 10, tzinfo=timezone.utc),
        datetime(2026, 10, 12, 10, tzinfo=timezone.utc),
        datetime(2026, 10, 20, 10, tzinfo=timezone.utc),
    ]
    with db.get_session() as session:
        session.add_all([
            NoteNode(name=f"Range Note {index}", is_folder=False, content=f"Range content {index}",
                     created_at=created, updated_at=created)
            for index, created in enumerate(dates, start=1)
        ])
        session.commit()

    response = coach.process_query("Show notes from 2026-10-09 through 2026-10-15")

    assert "Range Note 1" in response
    assert "Range Note 2" in response
    assert "Range Note 3" not in response

# 4. Return useful response when no notes exist for the requested period
def test_no_notes_for_requested_period(test_setup):
    coach = test_setup["coach"]
    response = coach.process_query("What notes did I write on 2022-01-01?")
    assert "No notes" in response or "no notes" in response.lower()
    assert len(response.strip()) > 0

# 5. Calculate study time for each of the last four weeks
def test_calculate_study_time_last_four_weeks(test_setup):
    db = test_setup["db"]
    coach = test_setup["coach"]
    analytics = test_setup["analytics"]

    now = datetime.now(timezone.utc)

    # Week 4 (current week)
    s4 = StudySession(start_time=now - timedelta(days=1), duration_seconds=7200, status="COMPLETED", topic="Python", session_type="stopwatch")
    # Week 3 (1 week ago)
    s3 = StudySession(start_time=now - timedelta(days=8), duration_seconds=3600, status="COMPLETED", topic="Math", session_type="stopwatch")
    # Week 2 (2 weeks ago) - 0 hours
    # Week 1 (3 weeks ago)
    s1 = StudySession(start_time=now - timedelta(days=22), duration_seconds=5400, status="COMPLETED", topic="Python", session_type="stopwatch")

    with db.get_session() as session:
        session.add_all([s4, s3, s1])
        session.commit()

    weeks = analytics.get_week_by_week_analysis(num_weeks=4)
    assert len(weeks) == 4

    response = coach.process_query("I want a week-by-week analysis for the last 4 weeks of my studies.")
    assert "4-Week" in response or "Week" in response
    assert len(response.strip()) > 0

# 6. Handle weeks with zero study time
def test_handle_weeks_with_zero_study_time(test_setup):
    analytics = test_setup["analytics"]
    weeks = analytics.get_week_by_week_analysis(num_weeks=4)

    # All weeks empty initially
    for w in weeks:
        assert w["is_zero_study"] is True
        assert w["total_seconds"] == 0
        assert "0m" in w["formatted_duration"] or w["total_seconds"] == 0

# 7. Group study time by subject
def test_group_study_time_by_subject(test_setup):
    db = test_setup["db"]
    analytics = test_setup["analytics"]
    coach = test_setup["coach"]

    now = datetime.now(timezone.utc)
    with db.get_session() as session:
        s1 = StudySession(start_time=now, duration_seconds=3600, status="COMPLETED", topic="Physics", session_type="stopwatch")
        s2 = StudySession(start_time=now, duration_seconds=7200, status="COMPLETED", topic="Python", session_type="stopwatch")
        s3 = StudySession(start_time=now, duration_seconds=1800, status="COMPLETED", topic="Physics", session_type="stopwatch")
        session.add_all([s1, s2, s3])
        session.commit()

    breakdown = analytics.get_subject_breakdown()
    assert "Python" in breakdown["by_subject"]
    assert "Physics" in breakdown["by_subject"]
    assert breakdown["by_subject"]["Python"]["duration_seconds"] == 7200
    assert breakdown["by_subject"]["Physics"]["duration_seconds"] == 5400
    assert breakdown["most_studied"]["subject"] == "Python"

    response = coach.process_query("What is my study time by subject?")
    assert "Python" in response
    assert "Physics" in response

def test_calculate_study_time_for_explicit_date_range(test_setup):
    db = test_setup["db"]
    coach = test_setup["coach"]
    with db.get_session() as session:
        session.add_all([
            StudySession(start_time=datetime(2026, 10, 10, 10, tzinfo=timezone.utc),
                         duration_seconds=3600, status="COMPLETED", topic="Physics", session_type="stopwatch"),
            StudySession(start_time=datetime(2026, 10, 12, 10, tzinfo=timezone.utc),
                         duration_seconds=1800, status="COMPLETED", topic="Physics", session_type="stopwatch"),
            StudySession(start_time=datetime(2026, 10, 20, 10, tzinfo=timezone.utc),
                         duration_seconds=7200, status="COMPLETED", topic="Math", session_type="stopwatch"),
        ])
        session.commit()

    response = coach.process_query("How much did I study from 2026-10-09 to 2026-10-15?")

    assert "2026-10-09" in response
    assert "2026-10-15" in response
    assert "1h 30m" in response
    assert "Math" not in response

def test_compare_study_time_across_two_date_ranges(test_setup):
    db = test_setup["db"]
    coach = test_setup["coach"]
    with db.get_session() as session:
        session.add_all([
            StudySession(start_time=datetime(2026, 10, 10, 10, tzinfo=timezone.utc),
                         duration_seconds=3600, status="COMPLETED", topic="Physics", session_type="stopwatch"),
            StudySession(start_time=datetime(2026, 10, 20, 10, tzinfo=timezone.utc),
                         duration_seconds=5400, status="COMPLETED", topic="Physics", session_type="stopwatch"),
        ])
        session.commit()

    response = coach.process_query(
        "Compare study time from 2026-10-09 to 2026-10-15 with 2026-10-19 to 2026-10-21"
    )

    assert "1h 0m" in response
    assert "1h 30m" in response
    assert "0h 30m more" in response

# 8. Answer question requiring both notes and study history
def test_answer_question_requiring_both_notes_and_study_history(test_setup):
    notes = test_setup["notes"]
    analytics = test_setup["analytics"]
    coach = test_setup["coach"]

    now = datetime.now(timezone.utc)
    with analytics.db.get_session() as session:
        s = StudySession(start_time=now, duration_seconds=3600, status="COMPLETED", topic="Machine Learning", session_type="stopwatch")
        session.add(s)
        session.commit()

    note = notes.create_node("ML Neural Nets", is_folder=False)
    notes.update_node_content(note.id, "Backpropagation details.")

    response = coach.process_query("What notes did I write today and what did I study?")
    assert "ML Neural Nets" in response or "Backpropagation" in response
    assert "Machine Learning" in response or "1h" in response

# 9. Handle unavailable LLM providers and empty/malformed responses
def test_handle_unavailable_llm_and_empty_response(test_setup):
    analytics = test_setup["analytics"]
    notes = test_setup["notes"]

    # Test with failing provider
    failing_agent = StudyCoachAgent(provider=FailingLLMProvider())
    coach_failing = CoachService(agent=failing_agent, analytics_service=analytics, note_service=notes)

    response = coach_failing.process_query("I want a week-by-week analysis for the last 4 weeks of my studies.")
    assert len(response.strip()) > 0
    assert "4-Week" in response or "Week" in response

    # Test with empty provider
    empty_agent = StudyCoachAgent(provider=EmptyLLMProvider())
    coach_empty = CoachService(agent=empty_agent, analytics_service=analytics, note_service=notes)
    response_empty = coach_empty.process_query("What notes did I write today?")
    assert len(response_empty.strip()) > 0
    assert "Notes" in response_empty or "No notes" in response_empty

# 10. Verify dates are interpreted using configured timezone
def test_timezone_boundary_interpretation(test_setup):
    db = test_setup["db"]
    notes = test_setup["notes"]

    # In UTC+05:30:
    # 2026-11-01 01:00:00 local time is 2026-10-31 19:30:00 UTC.
    late_utc = datetime(2026, 10, 31, 19, 30, tzinfo=timezone.utc)

    with db.get_session() as session:
        n = NoteNode(name="Late Night Note", is_folder=False, content="Late study", created_at=late_utc, updated_at=late_utc)
        study = StudySession(start_time=late_utc, duration_seconds=1800, status="COMPLETED",
                             topic="Late Study", session_type="stopwatch")
        session.add_all([n, study])
        session.commit()

    tz_530 = CustomTestTZ()

    # With UTC+5:30, target date 2026-11-01 MUST include the note
    nov1_notes = notes.get_notes_by_date("2026-11-01", tz=tz_530)
    names = [n["name"] for n in nov1_notes]
    assert "Late Night Note" in names

    # But in UTC timezone, target date 2026-11-01 should NOT include it (it was Oct 31 in UTC)
    utc_notes = notes.get_notes_by_date("2026-11-01", tz=timezone.utc)
    utc_names = [n["name"] for n in utc_notes]
    assert "Late Night Note" not in utc_names

    heatmap = test_setup["analytics"].get_yearly_heatmap_data(2026, tz=tz_530)
    assert heatmap[date(2026, 11, 1)] == 1800
