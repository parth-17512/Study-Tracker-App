from datetime import datetime, timezone
from app.services.analytics_service import AnalyticsService

class AITools:
    """Read-only wrappers for exposing application stats to the AI Agent."""
    
    def __init__(self):
        self.analytics = AnalyticsService()
        
    def get_today_stats(self) -> dict:
        """Returns the user's total study duration and session count for today."""
        today = datetime.now(timezone.utc).date()
        sessions = self.analytics.get_sessions_for_date(today)
        
        total_duration = sum(s.duration_seconds or 0 for s in sessions if s.status == "COMPLETED")
        return {
            "date": today.isoformat(),
            "session_count": len([s for s in sessions if s.status == "COMPLETED"]),
            "total_study_minutes": total_duration // 60
        }
        
    def get_week_stats(self) -> dict:
        """Returns the user's total study duration for the current week."""
        # Simple placeholder implementation relying on analytics service
        summary = self.analytics.get_weekly_summary()
        return {
            "total_study_minutes": summary.get("total_duration_seconds", 0) // 60,
            "best_day": summary.get("best_day_str", "Unknown")
        }
        
    def get_month_stats(self) -> dict:
        """Returns a summarized version of the user's monthly stats."""
        # Reuse weekly summary logic for simplicity in the foundation
        summary = self.analytics.get_weekly_summary()
        return {
            "status": "Monthly detailed stats are functionally similar to weekly for this prototype",
            "total_study_minutes_approx": (summary.get("total_duration_seconds", 0) // 60) * 4 
        }
        
    def get_streak(self) -> dict:
        """Returns the user's current consecutive daily study streak."""
        return {
            "current_streak_days": self.analytics.get_current_streak()
        }
        
    def get_recent_sessions(self, limit: int = 5) -> list:
        """Returns metadata about the user's most recent completed sessions."""
        recent = self.analytics.get_recent_sessions(limit)
        results = []
        for s in recent:
            if s.status == "COMPLETED":
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
