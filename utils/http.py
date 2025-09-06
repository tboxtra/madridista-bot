import requests
import time
import random

DEFAULT_TIMEOUT = 12
S = requests.Session()
S.headers.update({"User-Agent": "MadridistaBot/1.0 (+Telegram)"})

def get(url, *, params=None, headers=None, timeout=DEFAULT_TIMEOUT, retries=2, backoff=0.6):
    """HTTP GET with retries and backoff"""
    last = None
    for i in range(retries+1):
        try:
            r = S.get(url, params=params, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            last = e
            if i < retries:
                time.sleep(backoff + random.random()*0.5)
    raise last
