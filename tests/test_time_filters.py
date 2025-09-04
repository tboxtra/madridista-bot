from utils.timeutil import window_filter, fmt_abs, now_utc
from datetime import timedelta

def test_window_filter_excludes_far_future():
    now = now_utc()
    mk = lambda dt, st: {"utcDate": dt, "status": st, "homeTeam":{"name":"A"}, "awayTeam":{"name":"B"}}
    within = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    tomorrow = (now + timedelta(hours=26)).strftime("%Y-%m-%dT%H:%M:%SZ")
    nov = (now + timedelta(days=70)).strftime("%Y-%m-%dT%H:%M:%SZ")
    matches = [mk(within,"SCHEDULED"), mk(tomorrow,"TIMED"), mk(nov,"SCHEDULED")]
    out = window_filter(matches, days=2, max_days_cap=7)
    assert len(out) == 2 and out[0]["utcDate"] == within and out[1]["utcDate"] == tomorrow

def test_fmt_abs_returns_string():
    assert isinstance(fmt_abs("2025-09-04T18:00:00Z"), str)
