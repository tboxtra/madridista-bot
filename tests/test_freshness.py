from utils.freshness import is_fresh
from utils.timeutil import now_utc
from datetime import timedelta

def test_is_fresh_true():
    assert is_fresh(now_utc(), 120)

def test_is_fresh_false():
    assert not is_fresh(now_utc() - timedelta(minutes=5), 120)
