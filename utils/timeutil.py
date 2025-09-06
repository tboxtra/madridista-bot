from datetime import datetime, timezone, timedelta
import pytz
from typing import Optional

LAGOS = pytz.timezone("Africa/Lagos")

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def parse_iso_utc(iso: str) -> Optional[datetime]:
    try:
        # Handle "Z"
        if iso.endswith("Z"):
            iso = iso.replace("Z", "+00:00")
        return datetime.fromisoformat(iso).astimezone(timezone.utc)
    except Exception:
        return None

def to_local(dt: datetime) -> datetime:
    try:
        return dt.astimezone(LAGOS)
    except Exception:
        return dt

def fmt_abs(iso: str) -> str:
    dt = parse_iso_utc(iso) or now_utc()
    local = to_local(dt)
    # Example: Sat 13 Sep • 15:15
    return local.strftime("%a %d %b • %H:%M")

def is_fresh_iso(iso: str, days: int = 120) -> bool:
    dt = parse_iso_utc(iso)
    if not dt:
        return False
    return (now_utc() - dt) <= timedelta(days=days)
