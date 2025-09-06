from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

def now_utc() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)

def parse_iso_utc(iso_string: str) -> datetime:
    """Parse ISO 8601 UTC datetime string"""
    if iso_string.endswith('Z'):
        iso_string = iso_string[:-1] + '+00:00'
    return datetime.fromisoformat(iso_string)

def fmt_abs(iso_string: str) -> str:
    """Format absolute datetime for display"""
    try:
        dt = parse_iso_utc(iso_string)
        return dt.strftime("%a %d %b %H:%M")
    except Exception:
        return iso_string

def to_local(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to local timezone"""
    # For now, return as-is. In production, you might want to use a specific timezone
    return utc_dt

def window_filter(matches: List[Dict[str, Any]], days: int = 2, max_days_cap: int = 7) -> List[Dict[str, Any]]:
    """Filter matches within a time window"""
    now = now_utc()
    cutoff = now + timedelta(days=min(days, max_days_cap))
    
    filtered = []
    for match in matches:
        try:
            match_dt = parse_iso_utc(match.get("utcDate", ""))
            if now <= match_dt <= cutoff:
                filtered.append(match)
        except Exception:
            continue
    
    return filtered
