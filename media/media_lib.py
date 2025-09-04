import os, json, random

ENABLE = os.getenv("ENABLE_MEDIA", "false").lower() == "true"
REPLY_PROB = float(os.getenv("MEDIA_REPLY_PROB", "0.30"))

# load once
_memes = []
try:
    with open("assets/memes.json", "r", encoding="utf-8") as f:
        _memes = json.load(f)
except Exception:
    _memes = []

def pick_media_for(text):
    """Return a dict {type: 'img'|'gif', url: '...'} or None."""
    if not ENABLE or not _memes or random.random() > REPLY_PROB:
        return None
    t = text.lower()
    # simple tag rules
    if any(k in t for k in ["goal", "scores", "gol", "bellingham!"]):
        pool = [m for m in _memes if m["tag"] == "goal"]
    elif any(k in t for k in ["vinicius", "vini"]):
        pool = [m for m in _memes if m["tag"] == "vinicius"]
    elif any(k in t for k in ["ronaldo", "cr7"]):
        pool = [m for m in _memes if m["tag"] == "ronaldo"]
    elif any(k in t for k in ["hala", "madrid"]):
        pool = [m for m in _memes if m["tag"] == "hala"]
    elif any(k in t for k in ["barca", "barcelona"]):
        pool = [m for m in _memes if m["tag"] == "barca"]
    elif any(k in t for k in ["champions", "ucl"]):
        pool = [m for m in _memes if m["tag"] == "champions"]
    elif any(k in t for k in ["bernabeu", "stadium"]):
        pool = [m for m in _memes if m["tag"] == "bernabeu"]
    elif any(k in t for k in ["ancelotti", "carlo"]):
        pool = [m for m in _memes if m["tag"] == "ancelotti"]
    elif any(k in t for k in ["bellingham", "jude"]):
        pool = [m for m in _memes if m["tag"] == "bellingham"]
    elif any(k in t for k in ["celebration", "win", "victory"]):
        pool = [m for m in _memes if m["tag"] == "celebration"]
    else:
        pool = _memes
    return random.choice(pool) if pool else None
