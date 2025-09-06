# utils/relevance.py
import os, re
from typing import Tuple

# Controls
AUTO_REPLY = os.getenv("AUTO_REPLY", "true").lower() == "true"           # allow unsolicited replies in groups
AUTO_REPLY_PROB = float(os.getenv("AUTO_REPLY_PROB", "0.45"))            # base chance to jump in when relevant
REQUIRE_MENTION = os.getenv("REQUIRE_MENTION", "false").lower() == "true" # force @mention to reply
BOT_NAME = os.getenv("BOT_NAME", "").lower()  # set to handle mentions reliably

KEYS_FOOTBALL = (
    "madrid","real madrid","barca","barcelona","laliga","ucl","champions",
    "fixture","lineup","xi","goal","assist","injury","table","scorers",
    "prediction","predict","odds","h2h","form","news","transfer","rumor",
    "vinicius","vini","bellingham","ancelotti","mbapp","bernabeu"
)

def classify_relevance(text: str, is_group: bool) -> Tuple[bool, float, str]:
    """
    Returns (should_consider, confidence, reason).
    - should_consider: True if message is football-ish or mentions the bot
    - confidence: 0..1 heuristic
    """
    q = (text or "").lower()
    if not q.strip():
        return False, 0.0, "empty"

    mentioned = (BOT_NAME and f"@{BOT_NAME}" in q)
    football_hits = sum(1 for k in KEYS_FOOTBALL if k in q)

    if REQUIRE_MENTION and is_group and not mentioned:
        return False, 0.0, "mention_required"

    if mentioned:
        return True, 0.95, "mentioned"

    if football_hits >= 2:
        return True, min(0.8, 0.4 + 0.2*football_hits), "football_terms"
    if "who wins" in q or "predict" in q or "clear of" in q:
        return True, 0.7, "banter_intent"

    # Default: only consider in DMs
    if not is_group:
        return True, 0.9, "dm_default"

    return AUTO_REPLY, AUTO_REPLY_PROB if AUTO_REPLY else 0.0, "auto_reply_policy"
