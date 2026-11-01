from datetime import datetime, timezone

def to_local_time(dt: datetime, tz=None) -> datetime:
    """Converts a naive UTC or UTC-aware datetime to the local (or specified) timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if tz is not None:
        return dt.astimezone(tz)
    return dt.astimezone()
