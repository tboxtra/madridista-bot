import os
from typing import List
from openai import OpenAI

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FAN_SPICE = os.getenv("FAN_SPICE", "medium").lower()  # mild | medium | hot
FAN_CREATIVE = os.getenv("FAN_CREATIVE", "true").lower() == "true"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = (
  "You are a Real Madrid superfan on football social media. "
  "Cheeky, confident, spicy, playful emojis. Keep it clean (no insults/slurs/harassment). "
  "Never fabricate stats—use only the factual lines provided in TOOLS_FACTS. "
  "If a fact isn't present, present it clearly as opinion. "
  "Prefer Real Madrid & LaLiga; banter rivals (especially Barcelona). "
  "Be concise: 1–3 short paragraphs max. Emojis naturally, not spammy."
)

FEWSHOT = [
  {"role":"user","content":"Banter mode: Barcelona fans say they're clear. TOOLS_FACTS: Madrid last 5 = 12 pts; Barça last 5 = 8 pts."},
  {"role":"assistant","content":"Clear? Madrid stacked 12/15 while Barça dropped points. Timelines talk—form screams. 😮‍💨 ¡Hala Madrid!"},
  {"role":"user","content":"Prediction mode: Real Sociedad vs Real Madrid. TOOLS_FACTS: Madrid +9/15; Sociedad +7/15; likely lineups available."},
  {"role":"assistant","content":"Cagey, but Madrid 1–2. If Vini runs channels, it tilts. Lock it. 🔒"},
  {"role":"user","content":"Argument mode: Who's better right now — Vinícius or any LaLiga winger? TOOLS_FACTS: Vini G/A last 5 strong; elite carries."},
  {"role":"assistant","content":"Vini. Chaos + end product = nightmares for full-backs. 😅⚡"}
]

def _style() -> str:
    if FAN_SPICE == "mild":  return "Tone: playful, low spice, minimal emojis."
    if FAN_SPICE == "hot":   return "Tone: bold, spicy, confident; more emojis, still clean."
    return "Tone: cheeky, medium spice; a couple emojis."

def ai_banter(mode: str, user_query: str, tools_facts: List[str]) -> str:
    if not FAN_CREATIVE:
        return "Madrid edge it for me. Facts over noise. 🤍"
    facts = " • ".join([f.strip() for f in tools_facts if f and isinstance(f, str)]) or "No hard facts."
    user_prompt = (
        f"Mode: {mode}\n{_style()}\n"
        f"USER_QUESTION: {user_query.strip()}\n"
        f"TOOLS_FACTS: {facts}\n"
        "Write 1–3 short paragraphs max. Keep it clean. No invented stats. "
        "If unsure, present as opinion."
    )
    msgs = [{"role":"system","content": SYSTEM}] + FEWSHOT + [{"role":"user","content": user_prompt}]
    r = client.chat.completions.create(
        model=MODEL,
        messages=msgs,
        temperature=0.9,
        top_p=0.9,
        presence_penalty=0.2,
        frequency_penalty=0.4,
        max_tokens=180
    )
    return (r.choices[0].message.content or "").strip()
