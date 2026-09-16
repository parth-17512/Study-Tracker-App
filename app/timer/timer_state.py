from enum import Enum

class TimerState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TimerMode(str, Enum):
    STOPWATCH = "stopwatch"
    COUNTDOWN = "countdown"
