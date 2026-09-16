from datetime import datetime, timezone, timedelta
from app.services.analytics_service import AnalyticsService

class AITools:
    """Read-only wrappers for exposing application stats to the AI Agent."""
    
    def __init__(self):
        self.analytics = AnalyticsService()
        
    def get_today_stats(self) -> dict:
        """Returns the user's total study duration and session count for today."""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        with self.analytics.db.get_session() as session:
            sessions = self.analytics.session_repo.get_by_date_range(session, start_of_day, end_of_day)
            
        completed = [s for s in sessions if s.status == "COMPLETED"]
        total_duration = sum(s.duration_seconds or 0 for s in completed)
        
        return {
            "date": start_of_day.date().isoformat(),
            "session_count": len(completed),
            "total_study_minutes": total_duration // 60
        }
        
    def get_week_stats(self) -> dict:
        """Returns the user's total study duration for the trailing 7 days."""
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=7)
        
        with self.analytics.db.get_session() as session:
            sessions = self.analytics.session_repo.get_by_date_range(session, start_of_week, now)
            
        completed = [s for s in sessions if s.status == "COMPLETED"]
        total_duration = sum(s.duration_seconds or 0 for s in completed)
        
        return {
            "total_study_minutes": total_duration // 60,
            "session_count_this_week": len(completed)
        }
        
    def get_month_stats(self) -> dict:
        """Returns a summarized version of the user's trailing 30 days."""
        now = datetime.now(timezone.utc)
        start_of_month = now - timedelta(days=30)
        
        with self.analytics.db.get_session() as session:
            sessions = self.analytics.session_repo.get_by_date_range(session, start_of_month, now)
            
        completed = [s for s in sessions if s.status == "COMPLETED"]
        total_duration = sum(s.duration_seconds or 0 for s in completed)
        return {
            "total_study_minutes_approx": total_duration // 60 
        }
        
    def get_streak(self) -> dict:
        """Returns the user's current consecutive daily study streak."""
        return {
            "current_streak_days": self.analytics.calculate_current_streak(datetime.now(timezone.utc))
        }
        
    def get_recent_sessions(self, limit: int = 5) -> list:
        """Returns metadata about the user's most recent completed sessions."""
        recent = self.analytics.get_recent_sessions(limit)
        results = []
        for s in recent:
            results.append({
                "topic": s.topic or "Uncategorized",
                "duration_minutes": (s.duration_seconds or 0) // 60,
                "date": s.start_time.strftime("%Y-%m-%d") if s.start_time else "Unknown"
            })
        return results
        
    def get_subject_stats(self) -> dict:
        """Stub for future subject tracking."""
        return {"error": "Subject tracking is currently not implemented."}
        
    def get_goal_progress(self) -> dict:
        """Stub for future goal tracking."""
        return {"error": "Goal tracking is currently not implemented."}
