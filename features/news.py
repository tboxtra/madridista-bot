from providers.livescore_news import fetch_news_raw, normalize_items, madrid_filter

def _fmt_item(it) -> str:
    t = it.get("title","").strip() or "Untitled"
    u = it.get("url","").strip()
    s = it.get("source","").strip()
    p = it.get("published","").strip()
    line1 = f"• {t}"
    line2 = f"{s} • {p}" if s or p else ""
    if u:
        # Telegram auto-link (no markdown to avoid escaping)
        return f"{line1}\n{line2}\n{u}"
    return f"{line1}\n{line2}".strip()

def news_handler() -> str:
    try:
        raw = fetch_news_raw()
        items = normalize_items(raw)
        madrid = madrid_filter(items)
        picks = madrid[:6] if madrid else items[:6]
        if not picks:
            return "No fresh news found right now."
        lines = ["**Latest Madrid News**"]
        for it in picks:
            lines.append(_fmt_item(it))
        return "\n\n".join(lines)
    except Exception as e:
        return f"Could not fetch news right now. ({e})"
