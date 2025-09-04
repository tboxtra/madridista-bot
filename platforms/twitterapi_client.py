import os, time, requests, pyotp

BASE = "https://api.twitterapi.io"

API_KEY     = os.getenv("TWITTERAPI_IO_KEY")
USERNAME    = os.getenv("TW_USERNAME")
PASSWORD    = os.getenv("TW_PASSWORD")
PROXY_URL   = os.getenv("PROXY_URL")  # e.g. http://user:pass@ip:port
TOTP_SECRET = os.getenv("TW_TOTP_SECRET")  # optional but recommended
TOTP_CODE   = os.getenv("TW_TOTP_CODE")    # only if you don't have the secret

def check_secrets():
    """Check if all required secrets are present. Call this before using the client."""
    missing = [k for k,v in {
        "TWITTERAPI_IO_KEY": API_KEY,
        "TW_USERNAME": USERNAME,
        "TW_PASSWORD": PASSWORD,
        "PROXY_URL": PROXY_URL
    }.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required secrets: {', '.join(missing)}")

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

def _fresh_totp():
    """Return a fresh 6-digit TOTP. Prefer TOTP_SECRET; else use TW_TOTP_CODE once."""
    if TOTP_SECRET:
        return pyotp.TOTP(TOTP_SECRET).now()
    if not TOTP_CODE:
        raise RuntimeError("No TOTP available. Set TW_TOTP_SECRET (preferred) or TW_TOTP_CODE.")
    return TOTP_CODE.strip()

def login_step1_get_login_data():
    """
    Step 3.1 from TwitterAPI.io docs
    POST /login with username, password, proxy -> returns session
    """
    check_secrets()
    url = f"{BASE}/login"
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "proxy": PROXY_URL
    }
    
    # Handle rate limiting for free tier (1 request every 5 seconds)
    import time
    time.sleep(6)  # Wait 6 seconds to ensure rate limit reset
    
    r = requests.post(url, json=payload, headers=HEADERS, proxies=PROXIES, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"login step1 failed: {r.status_code} - {r.text}")
    data = r.json()
    
    # Try different response field names
    session = data.get("session") or data.get("login_data") or data.get("token")
    if not session:
        raise RuntimeError(f"No session/login_data/token in response: {data}")
    return session

def login_step2_get_session(login_data: str, totp_code: str = None):
    """
    Step 3.2 Complete Authentication
    POST /login/2fa with login_data + totp -> returns session
    """
    # Use provided TOTP code or fall back to environment
    if totp_code is None:
        totp_code = _fresh_totp()
    
    url = f"{BASE}/login/2fa"
    payload = {
        "login_data": login_data,
        "totp_code": totp_code,
        "proxy": PROXY_URL
    }
    r = requests.post(url, json=payload, headers=HEADERS, proxies=PROXIES, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"login step2 (2FA) failed: {r.status_code} - {r.text}")
    data = r.json()
    session = data.get("session")
    if not session:
        raise RuntimeError(f"No session returned: {data}")
    return session

def create_tweet(session: str, text: str):
    """
    POST /create_tweet with session, text, proxy
    """
    check_secrets()
    url = f"{BASE}/tweet"
    payload = {
        "session": session,
        "text": text,
        "proxy": PROXY_URL
    }
    r = requests.post(url, json=payload, headers=HEADERS, proxies=PROXIES, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"create_tweet failed: {r.status_code} - {r.text}")
    return r.json()
