import os
from collections import deque
from typing import Dict, Deque, Tuple, List

ENABLE = os.getenv("ENABLE_MEMORY", "false").lower() == "true"
WINDOW = int(os.getenv("MEMORY_WINDOW", "20"))

# chat_id -> deque[(author, text)]
_MEMORY: Dict[int, Deque[Tuple[str, str]]] = {}

def push(chat_id: int, author: str, text: str) -> None:
    if not ENABLE or not text:
        return
    buf = _MEMORY.get(chat_id)
    if buf is None:
        buf = deque(maxlen=WINDOW)
        _MEMORY[chat_id] = buf
    buf.append((author[:40], text[:600]))

def get_context(chat_id: int, k: int = 8) -> List[Tuple[str, str]]:
    if not ENABLE:
        return []
    buf = _MEMORY.get(chat_id)
    if not buf:
        return []
    # return up to last k messages
    return list(buf)[-k:]
