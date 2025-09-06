# providers/sportmonks.py
import os
from utils.http import get
TOKEN = os.getenv("SPORTMONKS_TOKEN","")
BASE  = "https://api.sportmonks.com/v3/football"

def player_transfers(player_id):
    r = get(f"{BASE}/transfers", params={"api_token": TOKEN, "filter[player_id]": player_id})
    return r.json()
