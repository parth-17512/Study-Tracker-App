from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timezone, timedelta, date
from app.services.base_service import BaseService
from app.repositories.session_repository import SessionRepository
from app.database.models import StudySession
from app.utils.time_utils import to_local_time

class AnalyticsService(BaseService):
    def __init__(self, db=None):
        super().__init__(db)
        self.session_repo = SessionRepository()
        
    def get_daily_total_seconds(self, target_date: datetime) -> int:
        """Calculate total study seconds for a specific day."""
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
            all_sessions = self.session_repo.get_all_ordered_by_date(session)
            completed = [s for s in all_sessions if s.status == "COMPLETED"]
            return completed[:limit]

    def get_yearly_heatmap_data(self, year: int, tz=None) -> Dict[datetime.date, int]:
        """
        Fetch all completed sessions for a given year and group them by date.
        Returns a dictionary mapping date -> total study seconds.
        """
        target_tz = tz or datetime.now().astimezone().tzinfo
        start_of_year = datetime(year, 1, 1, tzinfo=target_tz).astimezone(timezone.utc)
        end_of_year = datetime(year + 1, 1, 1, tzinfo=target_tz).astimezone(timezone.utc) - timedelta(microseconds=1)

        heatmap_data = {}
        with self.db.get_session() as session:
            sessions = self.session_repo.get_by_date_range(session, start_of_year, end_of_year)
            for s in sessions:
                if s.status == "COMPLETED" and s.start_time:
                    d = to_local_time(s.start_time, tz=target_tz).date()
                    heatmap_data[d] = heatmap_data.get(d, 0) + (s.duration_seconds or 0)
                    
        return heatmap_data

    def get_monthly_study_data(self, year: int, month: int) -> Dict[datetime.date, int]:
        """
        Fetch all completed sessions for a given month and group them by date.
        Returns a dictionary mapping date -> total study seconds.
        """
        start_of_month = datetime(year, month, 1, tzinfo=timezone.utc)
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
            start_date = now - timedelta(days=6)
            start_dt = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            sessions = self.session_repo.get_by_date_range(session, start_dt, now + timedelta(days=1))
            
        data = {}
        for i in range(7):
            d = (now - timedelta(days=6-i)).date()
            data[d] = 0
            
        for s in sessions:
            if s.status == "COMPLETED" and s.start_time:
                d = s.start_time.date()
                if d in data:
                    data[d] += (s.duration_seconds or 0)
                    
        return data

    # --- Enhanced Structured Analytics for AI Coach (Requirement 5) ---

    def get_week_by_week_analysis(self, num_weeks: int = 4, reference_dt: Optional[datetime] = None, tz=None) -> List[Dict[str, Any]]:
        """
        Calculates study time for each of the last N weeks (default 4).
        Uses consistent Monday-to-Sunday boundaries in the target or local timezone.
        Returns chronologically sorted list from oldest week to current week.
        Distinguishes zero study time from missing data.
        """
        target_tz = tz or datetime.now().astimezone().tzinfo
        ref = reference_dt or datetime.now(timezone.utc)
        local_ref = to_local_time(ref, tz=target_tz)
        ref_date = local_ref.date()

        # Current week Monday (weekday: Monday is 0)
        current_monday = ref_date - timedelta(days=ref_date.weekday())

        results = []
        with self.db.get_session() as session:
            for w in range(num_weeks - 1, -1, -1):
                monday = current_monday - timedelta(weeks=w)
                sunday = monday + timedelta(days=6)

                # Local datetime bounds
                start_local = datetime(monday.year, monday.month, monday.day, 0, 0, 0, tzinfo=target_tz)
                end_local = datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59, 999999, tzinfo=target_tz)

                start_utc = start_local.astimezone(timezone.utc)
                end_utc = end_local.astimezone(timezone.utc)

                week_sessions = [
                    s for s in self.session_repo.get_by_date_range(session, start_utc, end_utc)
                    if s.status == "COMPLETED"
                ]

                total_sec = sum(s.duration_seconds or 0 for s in week_sessions)
                session_count = len(week_sessions)

                subjects = {}
                for s in week_sessions:
                    topic = s.topic or "Uncategorized"
                    subjects[topic] = subjects.get(topic, 0) + (s.duration_seconds or 0)

                h = total_sec // 3600
                m = (total_sec % 3600) // 60
                dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"

                if w == 0:
                    relative_label = "Current Week"
                elif w == 1:
                    relative_label = "Last Week"
                else:
                    relative_label = f"{w} Weeks Ago"

                results.append({
                    "week_number": num_weeks - w,
                    "label": f"Week {num_weeks - w} ({monday.strftime('%b %d')} - {sunday.strftime('%b %d, %Y')})",
                    "date_range": f"{monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}",
                    "relative_label": relative_label,
                    "start_date": monday.isoformat(),
                    "end_date": sunday.isoformat(),
                    "total_seconds": total_sec,
                    "total_minutes": total_sec // 60,
                    "total_hours": round(total_sec / 3600, 2),
                    "formatted_duration": dur_str,
                    "session_count": session_count,
                    "subjects": subjects,
                    "has_data": session_count > 0,
                    "is_zero_study": total_sec == 0
                })

        return results

    def get_subject_breakdown(self, start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calculates study time and metrics grouped by subject/topic.
        """
        with self.db.get_session() as session:
            if start_dt and end_dt:
                sessions = [s for s in self.session_repo.get_by_date_range(session, start_dt, end_dt) if s.status == "COMPLETED"]
            else:
                sessions = [s for s in self.session_repo.get_all_ordered_by_date(session) if s.status == "COMPLETED"]

            total_seconds = sum(s.duration_seconds or 0 for s in sessions)
            total_sessions = len(sessions)

            subject_map = {}
            for s in sessions:
                topic = s.topic or "Uncategorized"
                if topic not in subject_map:
                    subject_map[topic] = {"duration_seconds": 0, "session_count": 0}
                subject_map[topic]["duration_seconds"] += (s.duration_seconds or 0)
                subject_map[topic]["session_count"] += 1

        by_subject = {}
        for topic, data in subject_map.items():
            sec = data["duration_seconds"]
            pct = (sec / total_seconds * 100) if total_seconds > 0 else 0.0
            h = sec // 3600
            m = (sec % 3600) // 60
            dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"
            by_subject[topic] = {
                "duration_seconds": sec,
                "duration_minutes": sec // 60,
                "formatted_duration": dur_str,
                "session_count": data["session_count"],
                "percentage": round(pct, 1)
            }

        most_studied = None
        least_studied = None
        if by_subject:
            sorted_subjects = sorted(by_subject.items(), key=lambda x: x[1]["duration_seconds"], reverse=True)
            most_studied = {"subject": sorted_subjects[0][0], **sorted_subjects[0][1]}
            least_studied = {"subject": sorted_subjects[-1][0], **sorted_subjects[-1][1]}

        return {
            "total_seconds": total_seconds,
            "total_minutes": total_seconds // 60,
            "total_sessions": total_sessions,
            "by_subject": by_subject,
            "most_studied": most_studied,
            "least_studied": least_studied
        }

    def get_today_summary(self, reference_dt: Optional[datetime] = None, tz=None) -> Dict[str, Any]:
        """Returns study session metrics for today based on configured/local timezone."""
        target_tz = tz or datetime.now().astimezone().tzinfo
        ref = reference_dt or datetime.now(timezone.utc)
        local_ref = to_local_time(ref, tz=target_tz)
        today = local_ref.date()

        start_local = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=target_tz)
        end_local = datetime(today.year, today.month, today.day, 23, 59, 59, 999999, tzinfo=target_tz)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)

        with self.db.get_session() as session:
            sessions = [s for s in self.session_repo.get_by_date_range(session, start_utc, end_utc) if s.status == "COMPLETED"]
            total_seconds = sum(s.duration_seconds or 0 for s in sessions)
            subjects = {}
            for s in sessions:
                topic = s.topic or "Uncategorized"
                subjects[topic] = subjects.get(topic, 0) + (s.duration_seconds or 0)
            session_count = len(sessions)

        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        dur_str = f"{h}h {m}m" if h > 0 else f"{m}m"

        return {
            "date": today.isoformat(),
            "total_seconds": total_seconds,
            "total_minutes": total_seconds // 60,
            "formatted_duration": dur_str,
            "session_count": session_count,
            "subjects": subjects
        }

    def get_date_range_summary(self, start_date: date, end_date: date, tz=None) -> Dict[str, Any]:
        """Return deterministic completed-session totals for inclusive local dates."""
        if end_date < start_date:
            raise ValueError("End date must be on or after start date.")

        target_tz = tz or datetime.now().astimezone().tzinfo
        start_local = datetime(start_date.year, start_date.month, start_date.day, tzinfo=target_tz)
        end_exclusive_local = datetime(end_date.year, end_date.month, end_date.day, tzinfo=target_tz) + timedelta(days=1)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_exclusive_local.astimezone(timezone.utc) - timedelta(microseconds=1)

        with self.db.get_session() as session:
            sessions = [
                item for item in self.session_repo.get_by_date_range(session, start_utc, end_utc)
                if item.status == "COMPLETED"
            ]
            total_seconds = sum(item.duration_seconds or 0 for item in sessions)
            subjects: Dict[str, int] = {}
            for item in sessions:
                subject = item.topic or "Uncategorized"
                subjects[subject] = subjects.get(subject, 0) + (item.duration_seconds or 0)
            session_count = len(sessions)

        hours, remainder = divmod(total_seconds, 3600)
        duration = f"{hours}h {remainder // 60}m" if hours else f"{remainder // 60}m"
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_seconds": total_seconds,
            "total_minutes": total_seconds // 60,
            "formatted_duration": duration,
            "session_count": session_count,
            "has_data": session_count > 0,
            "subjects": subjects,
        }

    def get_study_time_comparison(self, start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> Dict[str, Any]:
        """Compares total study time between two arbitrary datetime intervals."""
        with self.db.get_session() as session:
            p1_sessions = [s for s in self.session_repo.get_by_date_range(session, start1, end1) if s.status == "COMPLETED"]
            p2_sessions = [s for s in self.session_repo.get_by_date_range(session, start2, end2) if s.status == "COMPLETED"]
            sec1 = sum(s.duration_seconds or 0 for s in p1_sessions)
            sec2 = sum(s.duration_seconds or 0 for s in p2_sessions)

        diff = sec2 - sec1
        pct = ((diff / sec1) * 100) if sec1 > 0 else (100.0 if sec2 > 0 else 0.0)

        return {
            "period1_seconds": sec1,
            "period2_seconds": sec2,
            "difference_seconds": diff,
            "percentage_change": round(pct, 1)
        }
