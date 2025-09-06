# utils/cooldown.py
import time
from typing import Dict

_COOLDOWN: Dict[int, float] = {}
WINDOW = 14.0  # seconds between unsolicited replies per chat

def can_speak(chat_id: int) -> bool:
    last = _COOLDOWN.get(chat_id, 0.0)
    return (time.time() - last) >= WINDOW

def mark_spoken(chat_id: int):
    _COOLDOWN[chat_id] = time.time()
