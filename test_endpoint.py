#!/usr/bin/env python3
"""
Simple endpoint test for TwitterAPI.io
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTERAPI_IO_KEY")
USERNAME = os.getenv("TW_USERNAME") 
PASSWORD = os.getenv("TW_PASSWORD")
PROXY_URL = os.getenv("PROXY_URL")

print(f"🔑 API Key: {API_KEY[:10]}...")
print(f"👤 Username: {USERNAME}")
print(f"🌐 Proxy: {PROXY_URL}")

BASE = "https://api.twitterapi.io"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# Test the exact endpoint we found working
endpoint = "/login"
print(f"\n🚀 Testing: {BASE}{endpoint}")

try:
    response = requests.post(
        f"{BASE}{endpoint}",
        json={
            "username": USERNAME,
            "password": PASSWORD,
            "proxy": PROXY_URL
        },
        headers=HEADERS,
        proxies=PROXIES,
        timeout=30
    )
    
    print(f"📡 Response: {response.status_code}")
    print(f"📄 Body: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
