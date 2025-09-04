import os, requests
from typing import Dict, List, Optional, Union

HOST = os.getenv("SOFA_RAPIDAPI_HOST", "sofascore.p.rapidapi.com")
KEY  = os.getenv("SOFA_RAPIDAPI_KEY")
# Make this optional for bot startup
# if not KEY:
#     raise RuntimeError("Missing SOFA_RAPIDAPI_KEY")

S = requests.Session()
S.headers.update({
    "x-rapidapi-host": HOST,
    "x-rapidapi-key": KEY,
    "accept": "application/json",
    "user-agent": "MadridistaBot/1.0"
})

BASE = f"https://{HOST}"

def get_available_countries(match_id: Union[int, str]) -> List[Dict]:
    """
    Returns a list of countries that have TV channels for this match.
    Each item commonly has: {countryCode, countryName}
    """
    if not KEY:
        return []
    
    url = f"{BASE}/tvchannels/get-available-countries"
    r = S.get(url, params={"matchId": str(match_id)}, timeout=20)
    r.raise_for_status()
    data = r.json()
    # Response shape may vary; normalize to list[dict]
    countries = data.get("data") or data.get("countries") or data
    if isinstance(countries, dict):
        countries = countries.get("countries", [])
    return countries or []

def get_channels_for_country(match_id: Union[int, str], country_code: str) -> List[Dict]:
    """
    Fetch channels for a specific country code (e.g., 'NG', 'ES').
    Endpoint: /tvchannels/get-list?matchId=...&countryCode=...
    Each item typically includes: name, provider, url, language, etc.
    """
    if not KEY:
        return []
    
    url = f"{BASE}/tvchannels/get-list"
    params = {"matchId": str(match_id), "countryCode": country_code.upper()}
    r = S.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    items = data.get("data") or data.get("channels") or data
    if isinstance(items, dict):
        items = items.get("channels", [])
    return items or []
