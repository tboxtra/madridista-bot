import re

_MD2 = r'[_*[\]()~`>#+\-=|{}.!]'
_MD_RE = re.compile(_MD2)

def md_escape(s: str) -> str:
    s = s or ""
    return _MD_RE.sub(lambda m: "\\" + m.group(0), s)

