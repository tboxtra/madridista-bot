import os, time, re, random
from telegram import Update
from telegram.ext import ContextTypes
from ai_engine.gpt_engine import banter_reply

ENABLE = os.getenv("ENABLE_BANTER", "false").lower() == "true"
GAP = int(os.getenv("BANTER_COOLDOWN_SEC", "45"))
UGAP = int(os.getenv("BANTER_PER_USER_COOLDOWN_SEC", "120"))
MAX_HOUR = int(os.getenv("BANTER_MAX_PER_HOUR", "15"))
REPLY_PROB = float(os.getenv("BANTER_REPLY_PROB", "0.6"))
KW = [k.strip().lower() for k in os.getenv("BANTER_KEYWORDS", "").split(",") if k.strip()]
RIVALS = [k.strip().lower() for k in os.getenv("BANTER_RIVALS", "").split(",") if k.strip()]

MENTION_PATTERN = re.compile(r"@(realmadrid|cr7|vini|vinicius|bellingham|ancelotti|mbappe|yourbotname)", re.I)

def _now():
    return int(time.time())

def _hit_counter(bot_data, chat_id):
    # rolling one-hour window count per chat
    key = f"banter_count::{chat_id}"
    rec = bot_data.get(key, {"start": _now(), "n": 0})
    if _now() - rec["start"] > 3600:
        rec = {"start": _now(), "n": 0}
    rec["n"] += 1
    bot_data[key] = rec
    return rec["n"]

def _can_speak(bot_data, chat_id, user_id):
    # global chat cooldown
    last_chat_t = bot_data.get(f"banter_last::{chat_id}", 0)
    if _now() - last_chat_t < GAP:
        return False
    # per-user cooldown
    last_user_t = bot_data.get(f"banter_user::{chat_id}::{user_id}", 0)
    if _now() - last_user_t < UGAP:
        return False
    # per-hour cap
    count = bot_data.get(f"banter_count::{chat_id}", {"start": _now(), "n": 0})
    if (_now() - count.get("start", 0) <= 3600) and count.get("n", 0) >= MAX_HOUR:
        return False
    return True

def _mark_spoke(bot_data, chat_id, user_id):
    bot_data[f"banter_last::{chat_id}"] = _now()
    bot_data[f"banter_user::{chat_id}::{user_id}"] = _now()
    _hit_counter(bot_data, chat_id)

def _matches_keywords(text):
    t = text.lower()
    if any(k in t for k in KW):
        return True
    if any(k in t for k in RIVALS):
        return True
    if MENTION_PATTERN.search(t):
        return True
    return False

def _too_toxic(text):
    # quick-and-dirty guard; keep it simple
    banned = ["idiot","kill","die","trash","stupid","hate"]
    t = text.lower()
    return any(b in t for b in banned)

async def chat_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ENABLE:
        return
    msg = update.message
    if not msg or not msg.text:
        return
    chat_id = update.effective_chat.id
    user_id = msg.from_user.id
    
    # Check if banter is enabled for this specific chat
    if not context.application.bot_data.get(f"banter_enabled::{chat_id}", True):
        return

    txt = msg.text.strip()
    # Don't argue with ourselves
    if msg.from_user.is_bot:
        return
    # Heuristic: skip long walls of text or forwarding
    if len(txt) > 500:
        return
    # Basic trigger check
    if not _matches_keywords(txt):
        # random small chance to chime in anyway if Madrid is mentioned vaguely
        if random.random() > 0.05:
            return

    # Cooldown & cap
    if not _can_speak(context.application.bot_data, chat_id, user_id):
        return
    if random.random() > REPLY_PROB:
        return

    # Build a small context: who said what
    author = msg.from_user.first_name or "fan"
    context_blob = f"{author} said: \"{txt}\""

    # Ask the LLM for a short banter line
    reply = banter_reply(context_blob)
    # Safety check on final output
    if _too_toxic(reply):
        reply = "Focus on football. 🤍"

    # Reply to the message directly (threads visually)
    try:
        await msg.reply_text(reply, reply_to_message_id=msg.message_id)
        _mark_spoke(context.application.bot_data, chat_id, user_id)
    except Exception:
        # ignore failures
        pass
