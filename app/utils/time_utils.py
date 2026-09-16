from datetime import datetime, timezone

def to_local_time(dt: datetime) -> datetime:
    """Converts a naive UTC or UTC-aware datetime to the local timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone()
