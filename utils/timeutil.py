import os
from datetime import datetime, timezone, timedelta

# Handle zoneinfo import for Python 3.8 compatibility
try:
    import zoneinfo
    Z = zoneinfo.ZoneInfo(os.getenv("TZ", "Africa/Lagos"))
except ImportError:
    # Fallback for Python 3.8
    import pytz
    Z = pytz.timezone(os.getenv("TZ", "Africa/Lagos"))

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def parse_iso_utc(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)

def to_local(dt_utc: datetime) -> datetime:
    return dt_utc.astimezone(Z)

def fmt_abs(iso: str) -> str:
    return to_local(parse_iso_utc(iso)).strftime("%a %d %b • %H:%M")

def window_filter(matches, days=2, max_days_cap=7):
    """Keep only SCHEDULED/TIMED in [now, now+days], never > max_days_cap."""
    now = now_utc()
    soon = now + timedelta(days=days)
    hard_cap = now + timedelta(days=max_days_cap)
    out = []
    for m in matches:
        status = m.get("status", "")
        if status not in {"SCHEDULED", "TIMED"}:
            continue
        try:
            dt = parse_iso_utc(m["utcDate"])
        except Exception:
            continue
        if now <= dt <= soon and dt <= hard_cap:
            out.append(m)
    out.sort(key=lambda x: x["utcDate"])
    return out
