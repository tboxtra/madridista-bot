import re

# More comprehensive markdown escape pattern
MD2 = r'[_*[\]()~`>#+\-=|{}.!]'

def md_escape(s: str) -> str:
    """Escape markdown special characters for Telegram"""
    return re.sub(MD2, lambda m: '\\' + m.group(0), s or "")

