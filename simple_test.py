#!/usr/bin/env python3
"""
Simple test to verify the working request format
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

# Test the exact endpoint that was working
endpoint = "/auth/login"
print(f"\n🚀 Testing: {BASE}{endpoint}")

# Wait to ensure rate limit reset
import time
print("⏳ Waiting 6 seconds for rate limit reset...")
time.sleep(6)

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
    
    if response.status_code == 200:
        print("🎯 SUCCESS! Login endpoint working!")
    elif response.status_code == 429:
        print("⏰ Rate limited - endpoint exists but too many requests")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
