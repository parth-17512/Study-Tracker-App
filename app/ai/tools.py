from datetime import datetime, timezone, timedelta
from app.services.analytics_service import AnalyticsService
from app.services.note_service import NoteService

class AITools:
    """Read-only wrappers for exposing application stats to the AI Agent."""
    
    def __init__(self):
        self.analytics = AnalyticsService()
        self.notes = NoteService()
        
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

    # --- Read-Only Notes Access (Phase 8) ---
    
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
        # Simple paragraph chunking for now
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
