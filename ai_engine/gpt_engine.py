import os
from openai import OpenAI

# Uses the modern OpenAI Python SDK style.
# Make sure OPENAI_API_KEY is set.
_client = None

def _get_client():
    """Lazy initialization of OpenAI client"""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

SYSTEM_STYLE = (
    "You are MadridistaAI, a Real Madrid superfan and expert. "
    "Tone: confident, passionate, knowledgeable, friendly, and helpful. "
    "Bias: pro-Real Madrid, but factual and informative. "
    "Knowledge: Deep understanding of Real Madrid history, players, matches, statistics, and current events. "
    "Style: Conversational, engaging, and directly answers user questions. "
    "Constraints: Keep outputs concise (ideally < 200 chars for chat, < 240 for tweets), "
    "avoid hashtags and links, emojis allowed, be specific and helpful."
)

def generate_short_post(user_prompt: str, max_chars: int = 240) -> str:
    """
    Generate a short social post or response aligned with our persona.
    Now better at understanding context and answering specific questions.
    """
    # Get client when needed
    client = _get_client()
    
    # Enhanced prompt for better context understanding
    enhanced_prompt = f"""
    User Question/Request: {user_prompt}
    
    Please provide a helpful, informative response about Real Madrid that directly addresses what they're asking. 
    Be specific, factual, and engaging. If they ask about a player, mention relevant stats or achievements. 
    If they ask about history, provide interesting facts. If they ask about current events, give recent updates.
    """
    
    # We ask the model to self-limit length; we also clamp later in code.
    messages = [
        {"role": "system", "content": SYSTEM_STYLE},
        {"role": "user", "content": f"Keep to <= {max_chars} characters.\n{enhanced_prompt}"}
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",  # cheaper alternative
        messages=messages,
        temperature=0.7,  # Slightly lower for more consistent responses
        max_tokens=150,  # plenty for ~200 characters
    )
    return resp.choices[0].message.content.strip()

def banter_reply(context_blob):
    """Generate short, witty banter for group chat replies"""
    prompt = (
        "You are a Real Madrid superfan. Reply with short, witty banter. "
        "Rules: 1) Be confident and playful, not toxic. "
        "2) Keep it under 200 characters. 3) No hashtags or links. "
        f"Context from the chat: {context_blob}"
    )
    
    try:
        return generate_short_post(prompt, max_chars=200)
    except Exception:
        return "Calma… champions DNA speaks for itself. 🤍"

def riff_short(prompt, fallback="Calma… Champions DNA talks. 🤍", max_tokens=80):
    """Generate a short, witty response for group chat"""
    try:
        return generate_short_post(prompt, max_chars=180)
    except Exception:
        return fallback
