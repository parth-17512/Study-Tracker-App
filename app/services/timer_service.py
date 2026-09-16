from typing import Optional
from app.services.base_service import BaseService
from app.repositories.timer_repository import TimerRepository
from app.database.models import StudySession
from app.timer.timer_engine import TimerEngine
from app.timer.timer_state import TimerState

class TimerService(BaseService):
    def __init__(self, db=None):
        super().__init__(db)
        self.repository = TimerRepository()
        self.engine = TimerEngine()
        
    def start_stopwatch(self, subject_id: int = None, topic: str = None, notes: str = None):
        """Starts a stopwatch and persists it."""
        self.engine.start_stopwatch(subject_id, topic, notes)
        self._persist_state()

    def start_countdown(self, duration_seconds: int, subject_id: int = None, topic: str = None, notes: str = None):
        """Starts a countdown and persists it."""
        self.engine.start_countdown(duration_seconds, subject_id, topic, notes)
        self._persist_state()

    def pause(self):
        """Pauses the active timer and persists it."""
        self.engine.pause()
        self._persist_state()

    def resume(self):
        """Resumes a paused timer and persists it."""
        self.engine.resume()
        self._persist_state()

    def complete(self):
        """Completes the timer, saves the session to the DB, and clears the active timer state."""
        self.engine.complete()
        
        # We need to save the completed study session
        with self.db.get_session() as session:
            new_session = StudySession(
                start_time=self.engine.start_time,
                end_time=self.engine.target_end_time if self.engine.mode.value == 'countdown' else self.engine.start_time, # For now just placeholder, it should be now()
                duration_seconds=self.engine.get_elapsed_seconds(),
                subject_id=self.engine.subject_id,
                topic=self.engine.topic,
                notes=self.engine.notes,
                session_type=self.engine.mode.value,
                status=self.engine.state.value
            )
            # Fix end_time
            from app.timer.timer_engine import utc_now
            new_session.end_time = utc_now()

            session.add(new_session)
            self.repository.clear_active(session)
            
        # Reset the engine so it's clean for the next run
        self.engine.reset()

    def cancel(self):
        """Cancels the timer, clears the active state."""
        self.engine.cancel()
        with self.db.get_session() as session:
            # Depending on business logic, we might save cancelled sessions, but spec says "discarded"
            # We'll just clear the active state
            self.repository.clear_active(session)
        self.engine.reset()

    def check_active_timer(self) -> bool:
        """Loads an active timer from the database on startup, returns True if one was found."""
        with self.db.get_session() as session:
            active_db = self.repository.get_active(session)
            if active_db:
                # We need to convert SQLAlchemy model to dict for load_state
                state_data = {
                    'state': active_db.state,
                    'mode': active_db.mode,
                    'start_time': active_db.start_time,
                    'target_end_time': active_db.target_end_time,
                    'paused_at': active_db.paused_at,
                    'accumulated_elapsed_seconds': active_db.accumulated_elapsed_seconds,
                    'subject_id': active_db.subject_id,
                    'topic': active_db.topic,
                    'notes': active_db.notes
                }
                
                self.engine.load_state(state_data)
                
                # If engine auto-completed a countdown, persist that
                if self.engine.state == TimerState.COMPLETED:
                    self.complete()
                    return False # We completed it, so no active timer to resume
                    
                return True
                
        return False

    def _persist_state(self):
        """Helper to write the current engine state to the database."""
        with self.db.get_session() as session:
            state_dict = self.engine.dump_state()
            # The TimerEngine handles the core data, we just pass it to repo
            self.repository.save_active(session, state_dict)
