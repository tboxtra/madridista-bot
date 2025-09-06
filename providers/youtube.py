# providers/youtube.py
import os
from utils.http import get
KEY = os.getenv("YOUTUBE_API_KEY","")

def latest_videos(channel_id, limit=5):
    r = get("https://www.googleapis.com/youtube/v3/search", params={
        "key": KEY, "channelId": channel_id, "order":"date", "part":"snippet", "maxResults": limit
    }, timeout=15)
    items = r.json().get("items", [])
    out = []
    for it in items:
        if it.get("id",{}).get("videoId"):
            out.append({
                "videoId": it["id"]["videoId"],
                "title": it["snippet"]["title"],
                "thumb": (it["snippet"]["thumbnails"] or {}).get("high",{}).get("url",""),
                "publishedAt": it["snippet"]["publishedAt"]
            })
    return out
