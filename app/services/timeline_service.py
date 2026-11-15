from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, Iterable, List, Optional

from sqlalchemy import and_, or_

from app.database.models import ActivityBlock, StudySession
from app.repositories.activity_repository import ActivityRepository
from app.services.base_service import BaseService


class TimelineValidationError(ValueError):
    """Raised when an activity block is invalid or overlaps existing recorded time."""


class TimelineService(BaseService):
    """Build and persist a local-calendar-day timeline from study and activity records."""

    def __init__(self, db=None):
        super().__init__(db)
        self.activity_repo = ActivityRepository()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _local_day_bounds(target_date: date):
        start_local = datetime.combine(target_date, time.min)
        end_local = datetime.combine(target_date + timedelta(days=1), time.min)
        return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)

    @staticmethod
    def _local_position(value: datetime, is_end: bool = False) -> int:
        local_value = value.astimezone()
        if is_end and local_value.hour == 0 and local_value.minute == 0 and local_value.second == 0:
            return 24 * 60 * 60
        return local_value.hour * 3600 + local_value.minute * 60 + local_value.second

    def _load_entries(self, session, target_date: date) -> List[Dict]:
        day_start_utc, day_end_utc = self._local_day_bounds(target_date)
        study_sessions = session.query(StudySession).filter(
            StudySession.status == "COMPLETED",
            StudySession.start_time < day_end_utc,
            or_(
                StudySession.end_time > day_start_utc,
                and_(
                    StudySession.end_time.is_(None),
                    StudySession.start_time >= day_start_utc,
                ),
            ),
        ).order_by(StudySession.start_time.asc()).all()
        activity_blocks = self.activity_repo.get_by_date_range(
            session, day_start_utc, day_end_utc
        )

        entries = []
        for study in study_sessions:
            start_utc = self._as_utc(study.start_time)
            duration = max(0, int(study.duration_seconds or 0))
            if duration:
                end_utc = start_utc + timedelta(seconds=duration)
            elif study.end_time:
                end_utc = self._as_utc(study.end_time)
            else:
                continue

            clipped_start = max(start_utc, day_start_utc)
            clipped_end = min(end_utc, day_end_utc)
            if clipped_start >= clipped_end:
                continue
            entries.append({
                "category": "study",
                "name": study.topic or "Study session",
                "notes": study.notes or "",
                "start": clipped_start.astimezone(),
                "end": clipped_end.astimezone(),
                "duration_seconds": int((clipped_end - clipped_start).total_seconds()),
                "session_id": study.id,
                "block_id": None,
            })

        for block in activity_blocks:
            start_utc = max(self._as_utc(block.start_time), day_start_utc)
            end_utc = min(self._as_utc(block.end_time), day_end_utc)
            if start_utc >= end_utc:
                continue
            entries.append({
                "category": block.category,
                "name": block.name,
                "notes": block.notes or "",
                "start": start_utc.astimezone(),
                "end": end_utc.astimezone(),
                "duration_seconds": int((end_utc - start_utc).total_seconds()),
                "session_id": None,
                "block_id": block.id,
            })

        return entries

    @staticmethod
    def build_segments(entries: Iterable[Dict]) -> List[Dict]:
        """Return non-overlapping category segments plus explicit unallocated gaps."""
        normalized = []
        for entry in entries:
            start_second = TimelineService._local_position(entry["start"])
            end_second = TimelineService._local_position(entry["end"], is_end=True)
            if end_second <= start_second:
                continue
            normalized.append((start_second, end_second, entry))

        normalized.sort(key=lambda item: (
            item[0],
            0 if item[2]["category"] == "study" else 1,
            item[1],
        ))

        segments = []
        cursor = 0
        day_seconds = 24 * 60 * 60
        for start_second, end_second, entry in normalized:
            start_second = max(cursor, min(day_seconds, start_second))
            end_second = max(start_second, min(day_seconds, end_second))
            if start_second > cursor:
                segments.append({
                    "category": "unallocated",
                    "name": "Unallocated time",
                    "notes": "",
                    "start_seconds": cursor,
                    "end_seconds": start_second,
                    "duration_seconds": start_second - cursor,
                    "block_id": None,
                    "session_id": None,
                })
            if end_second > start_second:
                segment = dict(entry)
                segment["start_seconds"] = start_second
                segment["end_seconds"] = end_second
                segment["duration_seconds"] = end_second - start_second
                segments.append(segment)
                cursor = end_second

        if cursor < day_seconds:
            segments.append({
                "category": "unallocated",
                "name": "Unallocated time",
                "notes": "",
                "start_seconds": cursor,
                "end_seconds": day_seconds,
                "duration_seconds": day_seconds - cursor,
                "block_id": None,
                "session_id": None,
            })
        return segments

    def get_day_timeline(self, target_date: date) -> Dict:
        with self.db.get_session() as session:
            entries = self._load_entries(session, target_date)

        segments = self.build_segments(entries)
        totals = {"study": 0, "rest": 0, "other": 0, "unallocated": 0}
        for segment in segments:
            category = segment["category"]
            if category in totals:
                totals[category] += segment["duration_seconds"]

        categorized_total = totals["study"] + totals["rest"] + totals["other"]
        return {
            "date": target_date,
            "entries": entries,
            "segments": segments,
            "summary": {
                **totals,
                "categorized_total": categorized_total,
                "total_seconds": 24 * 60 * 60,
            },
        }

    @staticmethod
    def _to_local_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.astimezone()
        return value.astimezone()

    def _validate_block(self, session, target_date: date, category: str, name: str,
                        start_time: datetime, end_time: datetime,
                        exclude_block_id: Optional[int] = None) -> Dict:
        category = (category or "").strip().lower()
        name = (name or "").strip()
        if category not in ("rest", "other"):
            raise TimelineValidationError("Choose Rest or Other. Study blocks come from completed timer sessions.")
        if not name:
            raise TimelineValidationError("Enter an activity name.")

        start_local = self._to_local_datetime(start_time)
        end_local = self._to_local_datetime(end_time)
        if start_local.date() != target_date or end_local.date() != target_date:
            raise TimelineValidationError("Activity blocks must stay within the selected calendar day.")
        if end_local <= start_local:
            raise TimelineValidationError(
                "End time must be later than start time. Overnight blocks are not supported."
            )

        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)
        duration_seconds = int((end_utc - start_utc).total_seconds())
        if duration_seconds <= 0:
            raise TimelineValidationError("Activity duration must be greater than zero.")

        entries = self._load_entries(session, target_date)
        for entry in entries:
            if exclude_block_id is not None and entry["block_id"] == exclude_block_id:
                continue
            entry_start = self._as_utc(entry["start"])
            entry_end = self._as_utc(entry["end"])
            if entry_start < end_utc and entry_end > start_utc:
                label = "study session" if entry["category"] == "study" else "activity block"
                raise TimelineValidationError(
                    f"This activity overlaps an existing {label} ({entry['name']})."
                )

        return {
            "category": category,
            "name": name,
            "start_time": start_utc,
            "end_time": end_utc,
            "duration_seconds": duration_seconds,
        }

    def create_activity_block(self, target_date: date, category: str, name: str,
                              start_time: datetime, end_time: datetime,
                              notes: str = "") -> int:
        with self.db.get_session() as session:
            payload = self._validate_block(
                session, target_date, category, name, start_time, end_time
            )
            payload["notes"] = (notes or "").strip() or None
            block = self.activity_repo.create(session, payload)
            return block.id

    def update_activity_block(self, block_id: int, target_date: date, category: str,
                              name: str, start_time: datetime, end_time: datetime,
                              notes: str = "") -> bool:
        with self.db.get_session() as session:
            block = self.activity_repo.get_by_id(session, block_id)
            if block is None:
                return False
            payload = self._validate_block(
                session, target_date, category, name, start_time, end_time,
                exclude_block_id=block_id,
            )
            payload["notes"] = (notes or "").strip() or None
            self.activity_repo.update(block, payload)
            return True

    def delete_activity_block(self, block_id: int) -> bool:
        with self.db.get_session() as session:
            return self.activity_repo.delete(session, block_id)
