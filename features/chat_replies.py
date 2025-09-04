import os, time, re, random
from telegram import Update
from telegram.ext import ContextTypes
from ai_engine.gpt_engine import riff_short
from utils.memory import get_context
from media.media_lib import pick_media_for

ENABLE = os.getenv("ENABLE_BANTER", "false").lower() == "true"
GAP = int(os.getenv("BANTER_COOLDOWN_SEC", "45"))
UGAP = int(os.getenv("BANTER_PER_USER_COOLDOWN_SEC", "120"))
MAX_HOUR = int(os.getenv("BANTER_MAX_PER_HOUR", "15"))
REPLY_PROB = float(os.getenv("BANTER_REPLY_PROB", "0.55"))
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
    banned = ["idiot","kill","die","trash","stupid","hate","racist"]
    t = text.lower()
    return any(b in t for b in banned)

def _typing_delay_for(text):
    L = len(text)
    # ~human typing delay (shorter for small replies)
    return min(3.5, 0.6 + 0.015 * L + random.random())

async def chat_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ENABLE:
        return
    msg = update.message
    if not msg or not msg.text or msg.from_user.is_bot:
        return

    chat_id = update.effective_chat.id
    user_id = msg.from_user.id
    txt = msg.text.strip()

    # Check if banter is enabled for this specific chat
    if not context.application.bot_data.get(f"banter_enabled::{chat_id}", True):
        return

    # trigger check
    if not _matches_keywords(txt):
        if random.random() > 0.05:  # occasional pop-in
            return

    # cooldown
    if not _can_speak(context.application.bot_data, chat_id, user_id):
        return
    if random.random() > REPLY_PROB:
        return

    # build short context window
    turns = get_context(chat_id, k=6)
    # Format context into a tiny transcript
    convo = "\n".join([f"{a}: {t}" for (a, t) in turns[-5:]])
    user_line = f"{msg.from_user.first_name}: {txt}"
    transcript = (convo + ("\n" if convo else "") + user_line)[-1200:]

    # ask LLM for short witty reply
    prompt = (
        "You are a Real Madrid superfan in a Telegram group. "
        "Reply with short, witty, human banter. 1 sentence, <=180 chars, no hashtags/links, light emojis ok.\n\n"
        f"Conversation so far:\n{transcript}"
    )
    reply = riff_short(prompt, fallback="Calma… Champions DNA talks. 🤍", max_tokens=80)
    if _too_toxic(reply):
        reply = "Focus on football. 🤍"

    # look human: typing action + small delay
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    import asyncio
    await asyncio.sleep(_typing_delay_for(reply))

    # send reply (threaded)
    try:
        sent = await msg.reply_text(reply, reply_to_message_id=msg.message_id)
        _mark_spoke(context.application.bot_data, chat_id, user_id)
    except Exception:
        return

    # maybe attach a meme/gif, based on the message we replied to or our reply
    media = pick_media_for(txt + " " + reply)
    if media:
        try:
            if media["type"] == "gif":
                await context.bot.send_animation(chat_id=chat_id, animation=media["url"], reply_to_message_id=sent.message_id)
            else:
                await context.bot.send_photo(chat_id=chat_id, photo=media["url"], reply_to_message_id=sent.message_id)
        except Exception:
            pass
