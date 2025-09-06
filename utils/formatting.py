def md_escape(s: str) -> str:
    # Telegram Markdown (legacy) special chars: * _ ` [
    if not isinstance(s, str): return s
    return s.replace('*','').replace('_','').replace('`','').replace('[','')

