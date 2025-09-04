#!/usr/bin/env python3
"""
Find the correct TwitterAPI.io endpoints
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

# Test various endpoint patterns
endpoints_to_test = [
    "/login",
    "/auth/login", 
    "/twitter/login",
    "/user/login",
    "/api/login",
    "/v1/login",
    "/v2/login",
    "/account/login",
    "/session/login",
    "/oauth/login",
    "/login/twitter",
    "/twitter/auth",
    "/auth/twitter",
    "/api/v1/login",
    "/api/v2/login"
]

print(f"\n🚀 Testing multiple endpoint patterns...")

for endpoint in endpoints_to_test:
    try:
        print(f"\n📡 Testing: {BASE}{endpoint}")
        response = requests.post(
            f"{BASE}{endpoint}",
            json={
                "username": USERNAME,
                "password": PASSWORD,
                "proxy": PROXY_URL
            },
            headers=HEADERS,
            proxies=PROXIES,
            timeout=10
        )
        
        print(f"✅ Response: {response.status_code}")
        if response.status_code != 404:
            print(f"📄 Body: {response.text}")
            if response.status_code == 200:
                print(f"🎯 SUCCESS! Found working endpoint: {endpoint}")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Wait a bit to avoid rate limits
    import time
    time.sleep(1)
