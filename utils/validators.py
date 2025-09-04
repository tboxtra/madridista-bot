def clamp_tweet(text: str, max_chars: int = 280) -> str:
    """
    Ensures the tweet is within X's 280 char limit.
    If too long, trims cleanly and adds an ellipsis.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text
    safe = text[: max_chars - 1].rstrip()
    # Avoid cutting in the middle of a multi-byte char or emoji (simple safe trim)
    return safe[:-1] + "…" if len(safe) == max_chars - 1 else safe + "…"
