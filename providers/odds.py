# providers/odds.py
import os
from utils.http import get
KEY = os.getenv("ODDS_API_KEY","")

def prematch_odds(sport_key="soccer_epl", regions="eu", markets="h2h", date_format="iso"):
    r = get("https://api.the-odds-api.com/v4/sports/{}/odds".format(sport_key), params={
        "apiKey": KEY, "regions": regions, "markets": markets, "dateFormat": date_format
    })
    return r.json()
