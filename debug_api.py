#!/usr/bin/env python3
"""
Debug TwitterAPI.io API issues
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

# Test different base URLs
base_urls = [
    "https://api.twitterapi.io",
    "https://api.twitterapi.io/v1",
    "https://api.twitterapi.io/v2",
    "https://twitterapi.io/api",
    "https://twitterapi.io"
]

endpoints = ["/login", "/auth/login", "/v1/login"]

for base in base_urls:
    print(f"\n🌐 Testing base URL: {base}")
    
    for endpoint in endpoints:
        try:
            url = f"{base}{endpoint}"
            print(f"📡 Testing: {url}")
            
            response = requests.post(
                url,
                json={
                    "username": USERNAME,
                    "password": PASSWORD,
                    "proxy": PROXY_URL
                },
                headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
                proxies={"http": PROXY_URL, "https": PROXY_URL},
                timeout=10
            )
            
            print(f"✅ Response: {response.status_code}")
            if response.status_code != 404:
                print(f"📄 Body: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Wait to avoid rate limits
        import time
        time.sleep(2)
