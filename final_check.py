#!/usr/bin/env python3
"""
Final check to understand what's happening with the API
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

print(f"\n🚀 Final check of working endpoints...")

# Test the endpoints that were working earlier
endpoints = [
    "/session",
    "/user", 
    "/auth/login",
    "/login"
]

for endpoint in endpoints:
    print(f"\n📡 Testing: {endpoint}")
    
    try:
        # Test POST method
        response = requests.post(f"{BASE}{endpoint}", headers=HEADERS, proxies=PROXIES, timeout=10)
        print(f"  POST: {response.status_code}")
        if response.status_code != 404:
            print(f"    📄 Body: {response.text[:100]}...")
            
    except Exception as e:
        print(f"  POST: ❌ {e}")
    
    # Wait between requests
    import time
    time.sleep(3)
