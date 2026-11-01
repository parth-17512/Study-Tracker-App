from datetime import datetime, timezone, timedelta, date
from app.services.analytics_service import AnalyticsService
from app.services.note_service import NoteService

class AITools:
    """Read-only wrappers for exposing application stats and notes to the AI Agent."""
    
    def __init__(self, analytics: AnalyticsService = None, notes: NoteService = None):
        self.analytics = analytics or AnalyticsService()
        self.notes = notes or NoteService()
        
    def get_today_stats(self) -> dict:
        """Returns the user's total study duration, session count, and subjects for today."""
        summary = self.analytics.get_today_summary()
        return summary
        
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

    def get_week_by_week_stats(self, num_weeks: int = 4) -> dict:
        """Returns week-by-week analysis for the last N weeks with dates, totals, and subject breakdown."""
        weeks = self.analytics.get_week_by_week_analysis(num_weeks=num_weeks)
        return {
            "num_weeks": len(weeks),
            "weeks": weeks
        }
        
    def get_subject_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """Returns subject/topic distribution, including most and least studied subjects."""
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except Exception:
                pass
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            except Exception:
                pass
        return self.analytics.get_subject_breakdown(start_dt, end_dt)
        
    def get_goal_progress(self) -> dict:
        """Stub for future goal tracking."""
        return {"error": "Goal tracking is currently not implemented."}

    # --- Read-Only Notes Access (Requirement 5) ---
    
    def list_notes(self) -> dict:
        """Returns a list of all notes and folders."""
        nodes = self.notes.get_all_nodes()
        results = []
        for n in nodes:
            results.append({
                "id": n.id,
                "name": n.name,
                "is_folder": n.is_folder,
                "parent_id": n.parent_id
            })
        return {"nodes": results}
        
    def read_note(self, note_id: int) -> dict:
        """Reads the full content of a specific note by ID."""
        node = self.notes.get_note(note_id)
        if not node:
            return {"error": f"Note with ID {note_id} not found."}
        if node.is_folder:
            return {"error": f"ID {note_id} is a folder, not a note."}
            
        return {
            "id": node.id,
            "name": node.name,
            "content": node.content or ""
        }
        
    def search_notes(self, query: str) -> dict:
        """Searches notes for a specific query."""
        results = self.notes.search_notes(query)
        matches = []
        for n in results:
            matches.append({
                "id": n.id,
                "name": n.name,
                "content_preview": (n.content[:200] + "...") if n.content and len(n.content) > 200 else n.content
            })
        return {"matches": matches}
        
    def get_note_chunks(self, note_id: int) -> dict:
        """Returns the note content split into smaller chunks for easier reading."""
        node = self.notes.get_note(note_id)
        if not node:
            return {"error": f"Note with ID {note_id} not found."}
        if node.is_folder:
            return {"error": f"ID {note_id} is a folder, not a note."}
            
        content = node.content or ""
        chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
        return {
            "id": node.id,
            "name": node.name,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }

    def get_notes_today(self) -> dict:
        """Retrieves all notes created or edited today in the user's timezone."""
        today = date.today()
        notes = self.notes.get_notes_by_date(today)
        return {
            "date": today.isoformat(),
            "count": len(notes),
            "notes": notes
        }

    def get_notes_by_date(self, target_date: str) -> dict:
        """Retrieves notes created or edited on a specific past or present date (YYYY-MM-DD)."""
        notes = self.notes.get_notes_by_date(target_date)
        return {
            "date": target_date,
            "count": len(notes),
            "notes": notes
        }

    def get_notes_by_date_range(self, start_date: str, end_date: str) -> dict:
        """Retrieves notes created or edited across a date range."""
        notes = self.notes.get_notes_by_date_range(start_date, end_date)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "count": len(notes),
            "notes": notes
        }
