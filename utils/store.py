import json, os, threading

_LOCK = threading.Lock()
_PATH = os.getenv("SUBS_FILE", "./data/subscriptions.json")

def _ensure_dir():
    d = os.path.dirname(_PATH) or "."
    os.makedirs(d, exist_ok=True)

def load_subs() -> set:
    _ensure_dir()
    if not os.path.exists(_PATH):
        return set()
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_subs(subs: set) -> None:
    _ensure_dir()
    with _LOCK:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted(list(subs)), f)
