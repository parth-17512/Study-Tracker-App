import math
from datetime import datetime, timezone
from typing import Optional, Dict
from app.timer.timer_state import TimerState, TimerMode

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TimerEngine:
    """
    Core business logic for the study timer.
    Uses timestamps for accuracy, completely independent of the UI or databases.
    """
    
    def __init__(self):
        self.state: TimerState = TimerState.IDLE
        self.mode: TimerMode = TimerMode.STOPWATCH
        self.start_time: Optional[datetime] = None
        self.target_end_time: Optional[datetime] = None
        
        # Accumulates paused duration so elapsed time calculations remain accurate
        self.paused_at: Optional[datetime] = None
        self.accumulated_elapsed_seconds: int = 0
        self.target_duration: Optional[int] = None
        
        # Optional metadata
        self.subject_id: Optional[int] = None
        self.topic: Optional[str] = None
        self.notes: Optional[str] = None

    def start_stopwatch(self, subject_id: int = None, topic: str = None, notes: str = None):
        if self.state not in (TimerState.IDLE, TimerState.COMPLETED, TimerState.CANCELLED):
            raise ValueError(f"Cannot start stopwatch from state {self.state}")
            
        self.mode = TimerMode.STOPWATCH
        self.state = TimerState.RUNNING
        self.start_time = utc_now()
        self.target_end_time = None
        self.target_duration = None
        self.paused_at = None
        self.accumulated_elapsed_seconds = 0
        self.subject_id = subject_id
        self.topic = topic
        self.notes = notes

    def start_countdown(self, duration_seconds: int, subject_id: int = None, topic: str = None, notes: str = None):
        if self.state not in (TimerState.IDLE, TimerState.COMPLETED, TimerState.CANCELLED):
            raise ValueError(f"Cannot start countdown from state {self.state}")
            
        if duration_seconds <= 0:
            raise ValueError("Countdown duration must be greater than 0")
            
        self.mode = TimerMode.COUNTDOWN
        self.state = TimerState.RUNNING
        now = utc_now()
        self.start_time = now
        self.target_duration = duration_seconds
        self.target_end_time = datetime.fromtimestamp(now.timestamp() + duration_seconds, tz=timezone.utc)
        self.paused_at = None
        self.accumulated_elapsed_seconds = 0
        self.subject_id = subject_id
        self.topic = topic
        self.notes = notes

    def pause(self):
        if self.state != TimerState.RUNNING:
            raise ValueError(f"Cannot pause from state {self.state}")
            
        self.paused_at = utc_now()
        # Save exact elapsed time at moment of pause
        self.accumulated_elapsed_seconds = self.get_elapsed_seconds(self.paused_at)
        self.state = TimerState.PAUSED

    def resume(self):
        if self.state != TimerState.PAUSED:
            raise ValueError(f"Cannot resume from state {self.state}")
            
        now = utc_now()
        
        # When resuming, we effectively move the start_time forward by the amount of time we were paused
        # However, to avoid complexity, we just use the accumulated_elapsed_seconds.
        # So we reset start_time to `now` and keep the accumulated seconds.
        # For countdowns, we also need to shift the target_end_time forward.
        
        time_paused_seconds = (now - self.paused_at).total_seconds()
        
        self.start_time = now
        if self.mode == TimerMode.COUNTDOWN and self.target_end_time:
            self.target_end_time = datetime.fromtimestamp(self.target_end_time.timestamp() + time_paused_seconds, tz=timezone.utc)
            
        self.state = TimerState.RUNNING
        self.paused_at = None

    def complete(self):
        if self.state != TimerState.RUNNING:
            raise ValueError(f"Cannot complete from state {self.state}")
            
        # Update elapsed time one last time before finalizing
        self.accumulated_elapsed_seconds = self.get_elapsed_seconds()
        
        # Enforce exact completion duration for countdowns
        if self.mode == TimerMode.COUNTDOWN and self.target_duration:
            self.accumulated_elapsed_seconds = self.target_duration
            
        self.state = TimerState.COMPLETED

    def cancel(self):
        if self.state not in (TimerState.RUNNING, TimerState.PAUSED):
            raise ValueError(f"Cannot cancel from state {self.state}")
            
        self.accumulated_elapsed_seconds = self.get_elapsed_seconds()
        self.state = TimerState.CANCELLED

    def reset(self):
        """Returns the timer to IDLE state, clearing all data."""
        self.state = TimerState.IDLE
        self.start_time = None
        self.target_end_time = None
        self.target_duration = None
        self.paused_at = None
        self.accumulated_elapsed_seconds = 0

    def get_elapsed_seconds(self, reference_time: Optional[datetime] = None) -> int:
        """Returns the total elapsed time in seconds."""
        if self.state == TimerState.IDLE:
            return 0
            
        if self.state in (TimerState.COMPLETED, TimerState.CANCELLED, TimerState.PAUSED):
            return self.accumulated_elapsed_seconds
            
        now = reference_time or utc_now()
        if not self.start_time:
            return self.accumulated_elapsed_seconds
            
        # Accumulated time + time since last start/resume
        current_segment_elapsed = max(0.0, (now - self.start_time).total_seconds())
        elapsed = self.accumulated_elapsed_seconds + math.floor(current_segment_elapsed)
        
        # If countdown and elapsed exceeds target duration, cap it
        if self.mode == TimerMode.COUNTDOWN and self.target_duration:
            if elapsed >= self.target_duration:
                # To handle Bug B (59:59), we ensure it hits exactly the target
                return self.target_duration
        
        return elapsed

    def get_remaining_seconds(self) -> int:
        """Returns the remaining time in seconds for countdown mode. 0 for stopwatch."""
        if self.mode != TimerMode.COUNTDOWN or not self.target_end_time:
            return 0
            
        if self.state == TimerState.COMPLETED:
            return 0
            
        if self.state == TimerState.PAUSED:
            if not self.paused_at:
                return 0
            remaining = (self.target_end_time - self.paused_at).total_seconds()
            return max(0, math.floor(remaining))
            
        if self.state == TimerState.RUNNING:
            now = utc_now()
            remaining = (self.target_end_time - now).total_seconds()
            return max(0, math.floor(remaining))
            
        return 0

    def load_state(self, state_data: Dict):
        """Restores the engine state from a dictionary (e.g., from DB)."""
        self.state = TimerState(state_data['state'])
        self.mode = TimerMode(state_data['mode'])
        def ensure_tz(dt: Optional[datetime]) -> Optional[datetime]:
            if dt is not None and dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        self.start_time = ensure_tz(state_data.get('start_time'))
        self.target_end_time = ensure_tz(state_data.get('target_end_time'))
        self.target_duration = state_data.get('target_duration')
        self.paused_at = ensure_tz(state_data.get('paused_at'))
        
        self.accumulated_elapsed_seconds = state_data.get('accumulated_elapsed_seconds', 0)
        self.subject_id = state_data.get('subject_id')
        self.topic = state_data.get('topic')
        self.notes = state_data.get('notes')
        
        # If the app crashed while a countdown was running and the target time has passed
        if self.state == TimerState.RUNNING and self.mode == TimerMode.COUNTDOWN and self.target_end_time:
            if utc_now() >= self.target_end_time:
                self.complete()

    def dump_state(self) -> Dict:
        """Dumps the current state to a dictionary for persistence."""
        return {
            'state': self.state.value,
            'mode': self.mode.value,
            'start_time': self.start_time,
            'target_end_time': self.target_end_time,
            'target_duration': self.target_duration,
            'paused_at': self.paused_at,
            'accumulated_elapsed_seconds': self.accumulated_elapsed_seconds,
            'subject_id': self.subject_id,
            'topic': self.topic,
            'notes': self.notes
        }
