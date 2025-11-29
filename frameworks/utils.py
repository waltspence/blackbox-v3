from datetime import datetime, timedelta

def is_stale(timestamp_obj, max_age_hours: float = 1.0) -> bool:
    """
    Checks if a timestamp is older than max_age_hours.
    
    Args:
        timestamp_obj: Can be datetime object or ISO string.
    """
    if not timestamp_obj:
        return True
    
    now = datetime.utcnow()
    
    if isinstance(timestamp_obj, str):
        try:
            # Basic ISO parsing
            dt = datetime.fromisoformat(timestamp_obj.replace('Z', '+00:00'))
        except ValueError:
            return True  # Assume stale if parse fails
    else:
        dt = timestamp_obj
    
    # Ensure dt is timezone unaware for simple comparison or both aware
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    
    return (now - dt) > timedelta(hours=max_age_hours)
