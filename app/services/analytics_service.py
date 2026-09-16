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
            
            return completed[:limit]

    def get_yearly_heatmap_data(self, year: int) -> Dict[datetime.date, int]:
        """
        Fetch all completed sessions for a given year and group them by date.
        Returns a dictionary mapping date -> total study seconds.
        """
        start_of_year = datetime(year, 1, 1, tzinfo=timezone.utc)
        # Handle leap years automatically by going to next year
        end_of_year = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        
        heatmap_data = {}
        with self.db.get_session() as session:
            sessions = self.session_repo.get_by_date_range(session, start_of_year, end_of_year)
            for s in sessions:
                if s.status == "COMPLETED" and s.start_time:
                    d = s.start_time.date()
                    heatmap_data[d] = heatmap_data.get(d, 0) + (s.duration_seconds or 0)
                    
        return heatmap_data

    def get_monthly_study_data(self, year: int, month: int) -> Dict[datetime.date, int]:
        """
        Fetch all completed sessions for a given month and group them by date.
        Returns a dictionary mapping date -> total study seconds.
        """
        start_of_month = datetime(year, month, 1, tzinfo=timezone.utc)
        
        # Calculate start of next month
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_of_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
        monthly_data = {}
        with self.db.get_session() as session:
            sessions = self.session_repo.get_by_date_range(session, start_of_month, end_of_month)
            for s in sessions:
                if s.status == "COMPLETED" and s.start_time:
                    d = s.start_time.date()
                    monthly_data[d] = monthly_data.get(d, 0) + (s.duration_seconds or 0)
                    
        return monthly_data

    def get_summary_stats(self) -> dict:
        """Returns total sessions, total seconds, average session length, and best day."""
        with self.db.get_session() as session:
            sessions = [s for s in self.session_repo.get_all_ordered_by_date(session) if s.status == "COMPLETED"]
            
        total_sessions = len(sessions)
        if total_sessions == 0:
            return {"total_sessions": 0, "total_seconds": 0, "avg_session_seconds": 0, "best_day": None, "best_day_seconds": 0}
            
        total_seconds = sum(s.duration_seconds or 0 for s in sessions)
        avg_session_seconds = total_seconds // total_sessions
        
        # Calculate best day
        daily_totals = {}
        for s in sessions:
            if s.start_time:
                d = s.start_time.date()
                daily_totals[d] = daily_totals.get(d, 0) + (s.duration_seconds or 0)
                
        best_day = max(daily_totals.items(), key=lambda x: x[1]) if daily_totals else (None, 0)
        
        return {
            "total_sessions": total_sessions,
            "total_seconds": total_seconds,
            "avg_session_seconds": avg_session_seconds,
            "best_day": best_day[0],
            "best_day_seconds": best_day[1]
        }
        
    def get_period_comparisons(self, now: datetime) -> dict:
        """Compares this week vs last week, and this month vs last month."""
        with self.db.get_session() as session:
            sessions = [s for s in self.session_repo.get_all_ordered_by_date(session) if s.status == "COMPLETED"]
            
        # Very simple comparative bounds
        today = now.date()
        start_this_week = today - timedelta(days=today.weekday())
        start_last_week = start_this_week - timedelta(days=7)
        
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        this_week_sec = last_week_sec = this_month_sec = last_month_sec = 0
        
        for s in sessions:
            if not s.start_time:
                continue
            d = s.start_time.date()
            sec = s.duration_seconds or 0
            
            # Week
            if start_this_week <= d <= today:
                this_week_sec += sec
            elif start_last_week <= d < start_this_week:
                last_week_sec += sec
                
            # Month
            if d.year == this_month.year and d.month == this_month.month:
                this_month_sec += sec
            elif d.year == last_month.year and d.month == last_month.month:
                last_month_sec += sec
                
        return {
            "this_week": this_week_sec,
            "last_week": last_week_sec,
            "this_month": this_month_sec,
            "last_month": last_month_sec
        }
        
    def get_topic_distribution(self) -> Dict[str, int]:
        """Returns total seconds grouped by topic."""
        with self.db.get_session() as session:
            sessions = [s for s in self.session_repo.get_all_ordered_by_date(session) if s.status == "COMPLETED"]
            
        dist = {}
        for s in sessions:
            topic = s.topic or "Uncategorized"
            dist[topic] = dist.get(topic, 0) + (s.duration_seconds or 0)
        return dist
        
    def get_last_7_days_chart_data(self, now: datetime) -> Dict[datetime.date, int]:
        """Returns exact study durations for the last 7 days including today."""
        with self.db.get_session() as session:
            # We don't need all, just within last 7 days
            start_date = now - timedelta(days=6) # 6 days ago + today = 7 days
            start_dt = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            sessions = self.session_repo.get_by_date_range(session, start_dt, now + timedelta(days=1))
            
        data = {}
        # Pre-fill so all 7 days exist even if 0
        for i in range(7):
            d = (now - timedelta(days=6-i)).date()
            data[d] = 0
            
        for s in sessions:
            if s.status == "COMPLETED" and s.start_time:
                d = s.start_time.date()
                if d in data:
                    data[d] += (s.duration_seconds or 0)
                    
        return data
