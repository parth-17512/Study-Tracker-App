from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import StudySession
from app.repositories.base_repository import BaseRepository

class SessionRepository(BaseRepository[StudySession]):
    def __init__(self):
        super().__init__(StudySession)
        
    def get_all_ordered_by_date(self, session: Session) -> List[StudySession]:
        """Fetch all sessions ordered by start time (newest first)."""
        return session.query(StudySession).order_by(desc(StudySession.start_time)).all()
        
    def get_by_date_range(self, session: Session, start_date: datetime, end_date: datetime) -> List[StudySession]:
        """Fetch sessions within a specific date range."""
        return session.query(StudySession).filter(
            StudySession.start_time >= start_date,
            StudySession.start_time <= end_date
        ).order_by(desc(StudySession.start_time)).all()
