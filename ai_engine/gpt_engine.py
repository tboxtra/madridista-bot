import os
from openai import OpenAI

_client = OpenAI() if os.getenv("OPENAI_API_KEY") else None
AI_FLAIR = os.getenv("AI_FLAIR","false").lower()=="true"

SYSTEM = "You are a Real Madrid superfan. Keep replies short & grounded in provided data. No hashtags or links."

def riff_short(prompt: str, fallback: str, max_tokens: int = 80) -> str:
    if not _client or not AI_FLAIR:
        return fallback
    try:
        r = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":SYSTEM},
                      {"role":"user","content":prompt}],
            temperature=0.8, max_tokens=max_tokens
        )
        return (r.choices[0].message.content or "").strip() or fallback
    except Exception:
        return fallback
