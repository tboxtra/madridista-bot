# utils/http.py
import requests

def get(url, timeout=15, headers=None, params=None):
    r = requests.get(url, headers=headers or {}, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r

def post(url, json=None, timeout=15, headers=None):
    r = requests.post(url, json=json or {}, headers=headers or {}, timeout=timeout)
    r.raise_for_status()
    return r