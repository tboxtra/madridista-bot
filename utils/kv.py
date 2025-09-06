# tiny in-memory KV (per process). Replace with Redis/DB if needed.
_KV = {}

def kv_get(key: str):
    return _KV.get(key)

def kv_set(key: str, val):
    _KV[key] = val
