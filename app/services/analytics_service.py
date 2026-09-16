from typing import List, Dict, Tuple
from datetime import datetime, timezone, timedelta
from app.services.base_service import BaseService
from app.repositories.session_repository import SessionRepository
from app.database.models import StudySession

class AnalyticsService(BaseService):
    def __init__(self, db=None):
        super().__init__(db)
        self.session_repo = SessionRepository()
        
    def get_daily_total_seconds(self, target_date: datetime) -> int:
        """Calculate total study seconds for a specific day (UTC boundaries for now)."""
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        with self.db.get_session() as session:
            sessions = self.session_repo.get_by_date_range(session, start_of_day, end_of_day)
            total = sum((s.duration_seconds or 0) for s in sessions if s.status == "COMPLETED")
            return total

    def calculate_current_streak(self, today: datetime) -> int:
        """
        Calculate current contiguous daily streak.
        If the user studied today, it counts. If they didn't study today but studied yesterday, the streak is alive.
        If they didn't study today or yesterday, streak is 0.
        """
        with self.db.get_session() as session:
            all_sessions = self.session_repo.get_all_ordered_by_date(session)
            
        if not all_sessions:
            return 0
            
        # Extract unique dates where study occurred
        # We'll normalize to date strings for easy grouping
        study_dates = set()
        for s in all_sessions:
            if s.status == "COMPLETED" and s.start_time:
                study_dates.add(s.start_time.date())
                
        if not study_dates:
            return 0
            
        streak = 0
        current_date = today.date()
        
        # Check today
        if current_date in study_dates:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # If they didn't study today, check if they studied yesterday. 
            # If so, the streak is maintained (they have until end of today to increase it)
            current_date -= timedelta(days=1)
            if current_date not in study_dates:
                return 0
        
        # Count backwards
        while current_date in study_dates:
            streak += 1
            current_date -= timedelta(days=1)
            
        return streak

    def get_recent_sessions(self, limit: int = 3) -> List[StudySession]:
        """Fetch the most recent completed sessions."""
        with self.db.get_session() as session:
            # We fetch all and slice for simplicity, but a real repo should limit at the DB level.
            # We will just reuse our existing repo method here.
            all_sessions = self.session_repo.get_all_ordered_by_date(session)
            completed = [s for s in all_sessions if s.status == "COMPLETED"]
            
            # Detach them by doing something safe or rely on expire_on_commit=False
            return completed[:limit]
