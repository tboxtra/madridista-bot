#!/usr/bin/env python3
"""
Check TwitterAPI.io authentication and API status
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

# Test simple endpoint first
BASE = "https://api.twitterapi.io"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

print(f"\n🚀 Testing API connectivity...")

# Test 1: Simple GET request to check API status
try:
    print("📡 Testing API status...")
    response = requests.get(f"{BASE}/", headers=HEADERS, proxies=PROXIES, timeout=10)
    print(f"✅ Status response: {response.status_code}")
    print(f"📄 Body: {response.text[:200]}...")
except Exception as e:
    print(f"❌ Status check error: {e}")

# Test 2: Check if login endpoint exists with different methods
print(f"\n📡 Testing login endpoint with different methods...")

methods = ["GET", "POST", "OPTIONS"]
for method in methods:
    try:
        if method == "GET":
            response = requests.get(f"{BASE}/auth/login", headers=HEADERS, proxies=PROXIES, timeout=10)
        elif method == "POST":
            response = requests.post(f"{BASE}/auth/login", headers=HEADERS, proxies=PROXIES, timeout=10)
        elif method == "OPTIONS":
            response = requests.options(f"{BASE}/auth/login", headers=HEADERS, proxies=PROXIES, timeout=10)
            
        print(f"✅ {method} /auth/login: {response.status_code}")
        if response.status_code != 404:
            print(f"📄 Body: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ {method} error: {e}")
    
    import time
    time.sleep(2)  # Wait between requests
