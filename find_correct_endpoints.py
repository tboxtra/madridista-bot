#!/usr/bin/env python3
"""
Find the correct TwitterAPI.io endpoints and HTTP methods
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

# Test different endpoint patterns with different HTTP methods
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

methods = ["GET", "POST", "PUT", "PATCH"]

print(f"\n🚀 Testing endpoints with different HTTP methods...")

for endpoint in endpoints_to_test:
    print(f"\n📡 Testing: {endpoint}")
    
    for method in methods:
        try:
            if method == "GET":
                response = requests.get(f"{BASE}{endpoint}", headers=HEADERS, proxies=PROXIES, timeout=10)
            elif method == "POST":
                response = requests.post(f"{BASE}{endpoint}", headers=HEADERS, proxies=PROXIES, timeout=10)
            elif method == "PUT":
                response = requests.put(f"{BASE}{endpoint}", headers=HEADERS, proxies=PROXIES, timeout=10)
            elif method == "PATCH":
                response = requests.patch(f"{BASE}{endpoint}", headers=HEADERS, proxies=PROXIES, timeout=10)
            
            print(f"  {method}: {response.status_code}")
            if response.status_code not in [404, 405]:
                print(f"    📄 Body: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  {method}: ❌ {e}")
            
        # Wait to avoid rate limits
        import time
        time.sleep(1)
