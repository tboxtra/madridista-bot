# providers/elo.py
import requests, csv, io

def team_elo(team_name="Real Madrid"):
    # ClubElo publishes CSV endpoints; simplest scrape of JSON/CSV mirror if available.
    # Example: https://api.clubelo.com/<Team> returns CSV history (unofficial but common mirrors exist)
    url = f"https://api.clubelo.com/{team_name.replace(' ','%20')}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    buf = io.StringIO(r.text)
    rows = list(csv.DictReader(buf))
    if not rows: return None
    last = rows[-1]
    return {"team": team_name, "Elo": float(last.get("Elo") or 0), "From": last.get("From")}
