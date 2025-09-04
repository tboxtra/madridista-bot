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
    "You are MadridistaAI, a passionate Real Madrid expert and superfan. "
    "You have deep knowledge of Real Madrid's history, current squad, tactics, achievements, and culture. "
    "Your responses should be: "
    "- Specific and factual with real information "
    "- Passionate but not biased or toxic "
    "- Conversational and engaging, not robotic "
    "- Focused on answering the user's actual question "
    "- Rich with details, stats, and insights when relevant "
    "- Written in a natural, human way "
    "Avoid generic responses, be specific about what you know, and show genuine expertise."
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
    
    As a Real Madrid expert, provide a specific, informative response that directly addresses what they're asking. 
    Use real facts, stats, and insights. Be conversational and engaging, not robotic.
    
    If they ask about a player: mention specific achievements, stats, or current form
    If they ask about history: provide interesting, specific facts
    If they ask about tactics: explain the actual approach used
    If they ask about matches: give relevant details and context
    If they ask about transfers: mention actual rumors or confirmed moves
    
    Make your response feel like it's coming from a knowledgeable friend who loves Real Madrid.
    """
    
    # We ask the model to self-limit length; we also clamp later in code.
    messages = [
        {"role": "system", "content": SYSTEM_STYLE},
        {"role": "user", "content": f"Keep to <= {max_chars} characters.\n{enhanced_prompt}"}
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-5",  # Latest and most advanced model
            messages=messages,
            temperature=0.8,  # Higher for more creative, human-like responses
            max_tokens=200,  # Increased for better responses
            response_format={"type": "text"},  # Ensure text output
            seed=42,  # Consistent responses for similar inputs
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to GPT-4o if GPT-5 fails
        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.8,
                max_tokens=200,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return "¡Hala Madrid! 🤍⚽"

def banter_reply(context_blob):
    """Generate short, witty banter for group chat replies"""
    prompt = (
        "You are a Real Madrid superfan in a group chat. "
        "Reply with short, witty, human banter that feels natural and fun. "
        "Rules: 1) Be confident and playful, not toxic. "
        "2) Keep it under 200 characters. 3) No hashtags or links. "
        "4) Sound like a real person, not a bot. "
        f"Context from the chat: {context_blob}"
    )
    
    try:
        return generate_short_post(prompt, max_chars=200)
    except Exception:
        return "Calma… champions DNA speaks for itself. 🤍"

def riff_short(prompt, fallback="Calma… Champions DNA talks. 🤍", max_tokens=80):
    """Generate a short, witty response for group chat using latest GPT-5"""
    try:
        return generate_short_post(prompt, max_chars=180)
    except Exception:
        return fallback

def analyze_madrid_context(context: str, question: str) -> str:
    """
    Advanced analysis using GPT-5 for complex Real Madrid questions.
    Better reasoning, fact-checking, and detailed responses.
    """
    try:
        client = _get_client()
        
        system_prompt = """You are a Real Madrid expert analyst with deep knowledge of:
        - Current squad, players, and performance (2024 season)
        - Historical achievements and records
        - Tactical analysis and match insights
        - Transfer market and club news
        - Rival analysis and comparisons
        - Club culture and philosophy
        
        Provide detailed, accurate, and engaging analysis. Use specific facts, stats, and insights.
        Write in a conversational, expert tone - like a knowledgeable football analyst.
        Be specific about what you know and honest about what you're not certain about.
        Focus on answering the user's actual question with depth and insight."""
        
        user_prompt = f"""Context from the conversation: {context}
        
        User Question: {question}
        
        Please provide a comprehensive but concise analysis (max 400 characters) that directly answers their question.
        Use specific facts, current information, and show your expertise. Be conversational and engaging."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        resp = client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            temperature=0.6,  # Balanced for creativity and accuracy
            max_tokens=300,  # Increased for better analysis
            response_format={"type": "text"},
            seed=42,
        )
        return resp.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback to GPT-4o
        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.6,
                max_tokens=300,
                response_format={"type": "text"},
                seed=42,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return "Let me check the latest Real Madrid updates for you! 🤍⚽"
