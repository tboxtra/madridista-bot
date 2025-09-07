# utils/memory.py
from collections import deque
from typing import Deque, Dict, Tuple, List
import time, os
from openai import OpenAI

# Config knobs (override via env)
CTX_MAX_MSGS = int(os.getenv("CONTEXT_MAX_MSGS", "30"))       # raw messages kept per chat
CTX_SUMMARY_EVERY = int(os.getenv("CONTEXT_SUMMARY_EVERY", "20"))  # summarize after N msgs
SUMMARY_MAX_TOKENS = int(os.getenv("SUMMARY_MAX_TOKENS", "200"))

def _get_client():
    """Lazy initialization of OpenAI client"""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class ChatMemory:
    """
    Per-chat memory: short deque of recent messages + rolling summary.
    We store (role, text, timestamp, user_id, username).
    """
    def __init__(self, max_msgs: int = CTX_MAX_MSGS):
        self.max_msgs = max_msgs
        self.msgs: Deque[Tuple[str, str, float, int, str]] = deque(maxlen=max_msgs)
        self.summary: str = ""  # rolling abstract
        self.count_since_summary: int = 0

    def add(self, role: str, text: str, user_id: int, username: str = ""):
        self.msgs.append((role, (text or "").strip(), time.time(), int(user_id or 0), username or ""))
        self.count_since_summary += 1

    def should_summarize(self) -> bool:
        return self.count_since_summary >= CTX_SUMMARY_EVERY and len(self.msgs) >= 8

    def summarize_now(self):
        """Summarize current deque + prior summary (brief, football focus)."""
        if not self.msgs:
            return self.summary
        bullets = []
        for role, text, ts, uid, uname in list(self.msgs)[-CTX_SUMMARY_EVERY:]:
            tag = "U" if role == "user" else "B"
            name = uname or (str(uid) if uid else tag)
            bullets.append(f"{tag}({name}): {text}")
        prompt = (
            "Summarize the football conversation succinctly in 5-8 bullet points. "
            "Keep only on-topic details (teams, players, fixtures, stats, opinions), capture any asks or pending questions, "
            "and note the group's mood/banter tone briefly. Ignore greetings/off-topic chatter."
        )
        msgs = [
            {"role":"system","content":prompt},
            {"role":"user","content": "Previous Summary:\n" + (self.summary or "(none)")},
            {"role":"user","content": "Recent Messages:\n" + "\n".join(bullets)}
        ]
        try:
            r = _get_client().chat.completions.create(model=MODEL, messages=msgs, max_tokens=SUMMARY_MAX_TOKENS, temperature=0.2)
            out = (r.choices[0].message.content or "").strip()
            # Merge: keep latest as new summary (simple replace; could be concatenation)
            self.summary = out
            self.count_since_summary = 0
        except Exception:
            # Keep old summary on failure
            pass
        return self.summary

# Global in-process registry (swap to Redis/SQLite later if needed)
_MEM: Dict[int, ChatMemory] = {}  # chat_id -> memory

def mem_for(chat_id: int) -> ChatMemory:
    if chat_id not in _MEM:
        _MEM[chat_id] = ChatMemory()
    return _MEM[chat_id]

def export_context(chat_id: int) -> Dict:
    m = mem_for(chat_id)
    return {
        "summary": m.summary,
        "last_msgs": [{"role": r, "text": t, "user_id": uid, "username": name} for (r,t,_,uid,name) in m.msgs]
    }