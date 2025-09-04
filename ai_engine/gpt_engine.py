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
    "You are MadridistaAI, a Real Madrid superfan. "
    "Tone: confident, passionate, slightly cheeky, never toxic. "
    "Bias: pro-Real Madrid, Cristiano Ronaldo, Vinícius Jr. "
    "Constraints: keep outputs concise for social (ideally < 240 chars), "
    "avoid hashtags and links, emojis allowed."
)

def generate_short_post(user_prompt: str, max_chars: int = 240) -> str:
    """
    Generate a short social post aligned with our persona.
    """
    # Get client when needed
    client = _get_client()
    
    # We ask the model to self-limit length; we also clamp later in code.
    messages = [
        {"role": "system", "content": SYSTEM_STYLE},
        {"role": "user", "content": f"Keep to <= {max_chars} characters.\n{user_prompt}"}
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",  # cheaper alternative
        messages=messages,
        temperature=0.9,
        max_tokens=110,  # plenty for ~240 characters
    )
    return resp.choices[0].message.content.strip()
