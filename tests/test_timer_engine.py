import pytest
from datetime import datetime, timezone, timedelta
from app.timer.timer_engine import TimerEngine, TimerState, TimerMode

def test_stopwatch_basic_flow():
    engine = TimerEngine()
    assert engine.state == TimerState.IDLE
    
    engine.start_stopwatch()
    assert engine.state == TimerState.RUNNING
    assert engine.mode == TimerMode.STOPWATCH
    assert engine.start_time is not None
    
    # Simulate time passing for get_elapsed_seconds
    now = datetime.now(timezone.utc) + timedelta(seconds=5)
    assert engine.get_elapsed_seconds(reference_time=now) == 5
    
    engine.complete()
    assert engine.state == TimerState.COMPLETED
    assert engine.accumulated_elapsed_seconds >= 0

def test_countdown_basic_flow():
    engine = TimerEngine()
    engine.start_countdown(duration_seconds=10)
    
    assert engine.state == TimerState.RUNNING
    assert engine.mode == TimerMode.COUNTDOWN
    assert engine.target_end_time is not None
    
    # Check remaining time logic isn't negative
    remaining = engine.get_remaining_seconds()
    assert 0 <= remaining <= 10
    
    engine.cancel()
    assert engine.state == TimerState.CANCELLED

def test_pause_resume():
    engine = TimerEngine()
    engine.start_stopwatch()
    
    # Pause it
    engine.pause()
    assert engine.state == TimerState.PAUSED
    assert engine.paused_at is not None
    
    accumulated = engine.accumulated_elapsed_seconds
    
    # Wait, resume
    engine.resume()
    assert engine.state == TimerState.RUNNING
    assert engine.paused_at is None
    assert engine.accumulated_elapsed_seconds == accumulated # Should carry over

def test_invalid_transitions():
    engine = TimerEngine()
    
    with pytest.raises(ValueError):
        engine.pause() # Can't pause when IDLE
        
    with pytest.raises(ValueError):
        engine.resume() # Can't resume when IDLE
        
    engine.start_stopwatch()
    with pytest.raises(ValueError):
        engine.start_stopwatch() # Can't start while running


def test_timer_multiple_pause_resume():
    engine = TimerEngine()
    engine.start_stopwatch()
    
    # Study 20 minutes
    engine.start_time = datetime.now(timezone.utc) - timedelta(minutes=20)
    engine.pause()
    
    # Wait, resume
    engine.resume()
    
    # Study 40 minutes
    engine.start_time = datetime.now(timezone.utc) - timedelta(minutes=40)
    engine.complete()
    
    # Total elapsed should be 60 minutes = 3600 seconds
    assert engine.accumulated_elapsed_seconds == 3600

def test_timer_exact_one_hour():
    engine = TimerEngine()
    # If 3600 seconds countdown is started, and it naturally finishes exactly at 3600
    engine.start_countdown(3600)
    
    # Move start time exactly 3600 seconds ago
    engine.start_time = datetime.now(timezone.utc) - timedelta(seconds=3600)
    engine.complete()
    
    assert engine.accumulated_elapsed_seconds == 3600

def test_timer_cannot_exceed_target():
    engine = TimerEngine()
    engine.start_countdown(3600)
    
    # Timer completes while user is away (e.g. 1 hour and 40 minutes passed)
    engine.start_time = datetime.now(timezone.utc) - timedelta(minutes=100)
    engine.complete()
    
    # It should cap at 3600 seconds exactly
    assert engine.accumulated_elapsed_seconds == 3600

def test_notification_does_not_extend_timer():
    engine = TimerEngine()
    engine.start_countdown(3600)
    
    # Notification stays open for 10 extra minutes, then user dismisses which calls complete
    engine.start_time = datetime.now(timezone.utc) - timedelta(minutes=70)
    engine.complete()
    
    # The recorded duration is exactly 3600
    assert engine.accumulated_elapsed_seconds == 3600

def test_cancelled_timer_records_actual_duration():
    engine = TimerEngine()
    engine.start_countdown(3600)
    
    # Cancel after 25 minutes
    engine.start_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    engine.cancel()
    
    assert engine.state == TimerState.CANCELLED
    assert engine.accumulated_elapsed_seconds == 1500  # 25 * 60
