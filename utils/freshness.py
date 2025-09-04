from datetime import timedelta
from utils.timeutil import now_utc, to_local

def is_fresh(pulled_at_utc, max_age_s=120) -> bool:
    return pulled_at_utc is not None and (now_utc() - pulled_at_utc) <= timedelta(seconds=max_age_s)

def source_stamp(provider_name: str) -> str:
    return f"{provider_name} • {to_local(now_utc()).strftime('%H:%M:%S')}"
