from typing import List, Dict, Optional
from datetime import datetime
from app.services.base_service import BaseService
from app.repositories.session_repository import SessionRepository
from app.database.models import StudySession

class SessionService(BaseService):
    def __init__(self, db=None):
        super().__init__(db)
        self.repository = SessionRepository()
        
    def get_all_sessions(self) -> List[StudySession]:
        """Fetch all study sessions."""
        with self.db.get_session() as session:
            return self.repository.get_all_ordered_by_date(session)
            
    def get_session(self, session_id: int) -> Optional[StudySession]:
        """Fetch a specific study session."""
        with self.db.get_session() as session:
            # use standard get from base_repository
            return self.repository.get(session, session_id)
            
    def update_session(self, session_id: int, updates: Dict) -> Optional[StudySession]:
        """Update an existing study session (e.g. adjust duration, notes)."""
        # Validate data
        if 'duration_seconds' in updates and updates['duration_seconds'] < 0:
            raise ValueError("Duration cannot be negative.")
            
        with self.db.get_session() as session:
            db_obj = self.repository.get(session, session_id)
            if not db_obj:
                raise ValueError(f"Session {session_id} not found.")
                
            updated_obj = self.repository.update(session, db_obj, updates)
            # Have to map it to a format that doesn't expire when session closes
            # Or just return a boolean. Actually returning the object is fine if we eager load or just don't access lazy fields
            # For this simple app, we can just return True. We will re-fetch data in the UI anyway.
            return True
            
    def delete_session(self, session_id: int) -> bool:
        """Delete a study session."""
        with self.db.get_session() as session:
            return self.repository.delete(session, session_id)

    def search_sessions(self, text_query: str = None, topic: str = None, status: str = None, order_by: str = "newest") -> List[StudySession]:
        with self.db.get_session() as session:
            return self.repository.search_sessions(
                session, 
                text_query=text_query, 
                topic=topic, 
                status=status, 
                order_by=order_by
            )
