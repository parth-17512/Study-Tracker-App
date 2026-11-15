from datetime import date, datetime, time, timezone

import pytest

from app.database.database import Base, Database
from app.database.models import StudySession
from app.services.timeline_service import TimelineService, TimelineValidationError


@pytest.fixture
def timeline_service():
    database = Database("sqlite:///:memory:")
    Base.metadata.create_all(bind=database.engine)
    service = TimelineService(db=database)
    yield service, database
    database.engine.dispose()


def local_datetime(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute)).astimezone()


def add_study_session(database, day, start_hour, end_hour, topic="Math"):
    start = local_datetime(day, start_hour)
    end = local_datetime(day, end_hour)
    with database.get_session() as session:
        session.add(StudySession(
            start_time=start.astimezone(timezone.utc),
            end_time=end.astimezone(timezone.utc),
            duration_seconds=int((end - start).total_seconds()),
            topic=topic,
            session_type="stopwatch",
            status="COMPLETED",
        ))


def test_empty_day_is_all_unallocated(timeline_service):
    service, _ = timeline_service
    timeline = service.get_day_timeline(date(2026, 11, 15))

    assert len(timeline["segments"]) == 1
    assert timeline["segments"][0]["category"] == "unallocated"
    assert timeline["summary"]["unallocated"] == 86400
    assert timeline["summary"]["categorized_total"] == 0


def test_day_summary_includes_study_manual_blocks_and_gaps(timeline_service):
    service, database = timeline_service
    target_date = date(2026, 11, 15)
    add_study_session(database, target_date, 9, 10)

    service.create_activity_block(
        target_date, "rest", "Lunch",
        local_datetime(target_date, 10), local_datetime(target_date, 11),
    )
    service.create_activity_block(
        target_date, "other", "Walk",
        local_datetime(target_date, 11), local_datetime(target_date, 11, 30),
    )

    timeline = service.get_day_timeline(target_date)
    summary = timeline["summary"]

    assert summary["study"] == 3600
    assert summary["rest"] == 3600
    assert summary["other"] == 1800
    assert summary["categorized_total"] == 9000
    assert summary["unallocated"] == 77400
    assert sum(segment["duration_seconds"] for segment in timeline["segments"]) == 86400
    assert any(segment["category"] == "unallocated" for segment in timeline["segments"])


def test_rejects_activity_overlapping_study_or_another_activity(timeline_service):
    service, database = timeline_service
    target_date = date(2026, 11, 15)
    add_study_session(database, target_date, 9, 10)

    with pytest.raises(TimelineValidationError, match="overlaps an existing study session"):
        service.create_activity_block(
            target_date, "rest", "Break",
            local_datetime(target_date, 9, 30), local_datetime(target_date, 10, 30),
        )

    block_id = service.create_activity_block(
        target_date, "rest", "Break",
        local_datetime(target_date, 10), local_datetime(target_date, 11),
    )
    with pytest.raises(TimelineValidationError, match="overlaps an existing activity block"):
        service.create_activity_block(
            target_date, "other", "Walk",
            local_datetime(target_date, 10, 30), local_datetime(target_date, 11, 30),
        )

    assert service.update_activity_block(
        block_id, target_date, "rest", "Longer break",
        local_datetime(target_date, 10), local_datetime(target_date, 11),
    ) is True


def test_adjacent_blocks_are_allowed_and_invalid_day_bounds_rejected(timeline_service):
    service, _ = timeline_service
    target_date = date(2026, 11, 15)
    service.create_activity_block(
        target_date, "rest", "Break",
        local_datetime(target_date, 10), local_datetime(target_date, 11),
    )
    service.create_activity_block(
        target_date, "other", "Walk",
        local_datetime(target_date, 11), local_datetime(target_date, 12),
    )

    with pytest.raises(TimelineValidationError, match="End time must be later"):
        service.create_activity_block(
            target_date, "rest", "Invalid",
            local_datetime(target_date, 14), local_datetime(target_date, 14),
        )

    with pytest.raises(TimelineValidationError, match="selected calendar day"):
        service.create_activity_block(
            target_date, "rest", "Overnight",
            local_datetime(target_date, 23), local_datetime(date(2026, 11, 16), 1),
        )
