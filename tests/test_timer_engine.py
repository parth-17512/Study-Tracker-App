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
