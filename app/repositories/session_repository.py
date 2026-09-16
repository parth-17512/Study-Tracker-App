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

    def search_sessions(self, session: Session, text_query: str = None, 
                        topic: str = None, status: str = None, 
                        order_by: str = "newest") -> List[StudySession]:
        from sqlalchemy import or_, desc, asc
        
        query = session.query(StudySession)
        
        if text_query:
            wildcard_query = f"%{text_query}%"
            query = query.filter(
                or_(
                    StudySession.topic.ilike(wildcard_query),
                    StudySession.notes.ilike(wildcard_query)
                )
            )
            
        if topic and topic != "All":
            query = query.filter(StudySession.topic == topic)
            
        if status and status != "All":
            query = query.filter(StudySession.status == status)
            
        if order_by == "newest":
            query = query.order_by(desc(StudySession.start_time))
        elif order_by == "oldest":
            query = query.order_by(asc(StudySession.start_time))
        elif order_by == "longest":
            query = query.order_by(desc(StudySession.duration_seconds))
        elif order_by == "shortest":
            query = query.order_by(asc(StudySession.duration_seconds))
            
        return query.all()
