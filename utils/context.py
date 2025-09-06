"""
Conversation context management for group chats and context awareness.
"""
import time
from typing import Dict, List, Optional, Any
from collections import deque
from utils.kv import kv_get, kv_set

# Simple in-memory context storage (per chat)
CONTEXT_STORE = {}

def get_chat_context(chat_id: int, max_messages: int = 10) -> List[Dict[str, Any]]:
    """Get recent conversation context for a chat."""
    key = f"chat_context_{chat_id}"
    context = CONTEXT_STORE.get(key, deque(maxlen=max_messages))
    return list(context)

def add_to_context(chat_id: int, message: Dict[str, Any], max_messages: int = 10):
    """Add a message to chat context."""
    key = f"chat_context_{chat_id}"
    if key not in CONTEXT_STORE:
        CONTEXT_STORE[key] = deque(maxlen=max_messages)
    
    CONTEXT_STORE[key].append({
        "timestamp": time.time(),
        "user_id": message.get("user_id"),
        "username": message.get("username"),
        "text": message.get("text", ""),
        "is_bot": message.get("is_bot", False)
    })

def should_respond_in_group(chat_id: int, message_text: str, is_mentioned: bool = False) -> bool:
    """
    Determine if bot should respond in a group chat.
    Returns True if:
    - Bot is mentioned (@botname)
    - Message is a direct command
    - Message contains football keywords and bot hasn't spoken recently
    - Message is a reply to bot's previous message
    """
    if is_mentioned:
        return True
    
    # Check if it's a command
    if message_text.startswith('/'):
        return True
    
    # Check for football keywords
    football_keywords = [
        "madrid", "barcelona", "barca", "real madrid", "laliga", "champions",
        "fixture", "match", "game", "goal", "score", "lineup", "form",
        "predict", "compare", "table", "scorers", "news", "injury", "banter",
        "clear of", "vs", "versus", "who's better", "prediction"
    ]
    
    message_lower = message_text.lower()
    has_football_keywords = any(keyword in message_lower for keyword in football_keywords)
    
    if not has_football_keywords:
        return False
    
    # Check recent context to avoid spam
    context = get_chat_context(chat_id)
    recent_bot_messages = [
        msg for msg in context[-5:]  # Last 5 messages
        if msg.get("is_bot", False) and (time.time() - msg.get("timestamp", 0)) < 300  # 5 minutes
    ]
    
    # Don't respond if bot spoke recently (unless mentioned)
    if len(recent_bot_messages) > 0:
        return False
    
    # Check for high-priority football discussions
    high_priority_keywords = [
        "madrid", "barcelona", "barca", "real madrid", "laliga", "champions",
        "predict", "compare", "vs", "versus", "who's better", "clear of"
    ]
    
    has_high_priority = any(keyword in message_lower for keyword in high_priority_keywords)
    
    # Be more selective in group chats - only respond to high-priority football topics
    return has_high_priority

def extract_context_summary(chat_id: int) -> str:
    """Extract a brief summary of recent conversation context."""
    context = get_chat_context(chat_id, max_messages=5)
    if not context:
        return ""
    
    recent_topics = []
    for msg in context[-3:]:  # Last 3 messages
        text = msg.get("text", "").lower()
        if any(word in text for word in ["madrid", "barcelona", "barca"]):
            recent_topics.append("Madrid/Barca discussion")
        elif any(word in text for word in ["fixture", "match", "game"]):
            recent_topics.append("fixture discussion")
        elif any(word in text for word in ["predict", "prediction"]):
            recent_topics.append("prediction discussion")
        elif any(word in text for word in ["compare", "vs", "versus"]):
            recent_topics.append("comparison discussion")
    
    if recent_topics:
        return f"Recent context: {'; '.join(set(recent_topics))}"
    return ""

def is_group_chat(chat_type: str) -> bool:
    """Check if chat is a group."""
    return chat_type in ["group", "supergroup"]

def is_private_chat(chat_type: str) -> bool:
    """Check if chat is private."""
    return chat_type == "private"
