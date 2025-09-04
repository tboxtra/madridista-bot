import os
from typing import Optional
from providers.sofa_tv import get_available_countries, get_channels_for_country

USER_CC = os.getenv("USER_COUNTRY", "NG").upper()

def _fmt_channel(ch: dict) -> str:
    # Common keys (varies by feed): name, provider, language, webUrl
    name = ch.get("name") or ch.get("channelName") or "Channel"
    prov = ch.get("provider") or ch.get("broadcaster") or ""
    lang = ch.get("language") or ""
    url  = ch.get("webUrl") or ch.get("url") or ""
    bits = [name]
    if prov: bits.append(f"({prov})")
    if lang: bits.append(f"[{lang}]")
    line = " ".join(bits)
    if url:  # let Telegram auto-link
        return f"• {line}\n{url}"
    return f"• {line}"

def tv_handler(match_id: Optional[str]) -> str:
    if not match_id:
        return "Send a match id: `/tv 13157877`"  # keep simple; you can auto-detect later

    try:
        # 1) countries with coverage
        countries = get_available_countries(match_id)
        if not countries:
            return "No broadcast info found for that match."

        # 2) prefer USER_COUNTRY if present, else show the first 1–2
        ccodes = {c.get("countryCode", "").upper(): c for c in countries if c.get("countryCode")}
        chosen = USER_CC if USER_CC in ccodes else (next(iter(ccodes)) if ccodes else None)
        if not chosen:
            return "No valid country codes returned for this match."

        # 3) fetch channels for chosen country
        channels = get_channels_for_country(match_id, chosen)
        if not channels:
            return f"No TV channels listed for {chosen}."

        lines = [f"**Where to watch (Country: {chosen})**"]
        for ch in channels[:10]:
            lines.append(_fmt_channel(ch))
        return "\n\n".join(lines)
    except Exception as e:
        return f"Could not fetch TV listings right now. ({e})"
