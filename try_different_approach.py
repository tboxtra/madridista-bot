#!/usr/bin/env python3
"""
Try different approaches based on TwitterAPI.io documentation
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

# Try different approaches based on common API patterns
print(f"\n🚀 Trying different approaches...")

# Approach 1: Check if we need to authenticate first
print(f"\n📡 Approach 1: Check authentication endpoint")
try:
    response = requests.get(f"{BASE}/auth", headers=HEADERS, proxies=PROXIES, timeout=10)
    print(f"✅ /auth: {response.status_code}")
    if response.status_code != 404:
        print(f"📄 Body: {response.text[:100]}...")
except Exception as e:
    print(f"❌ /auth error: {e}")

# Approach 2: Try session-based login
print(f"\n📡 Approach 2: Try session endpoint")
try:
    response = requests.post(f"{BASE}/session", headers=HEADERS, proxies=PROXIES, timeout=10)
    print(f"✅ /session: {response.status_code}")
    if response.status_code != 404:
        print(f"📄 Body: {response.text[:100]}...")
except Exception as e:
    print(f"❌ /session error: {e}")

# Approach 3: Try user endpoint
print(f"\n📡 Approach 3: Try user endpoint")
try:
    response = requests.post(f"{BASE}/user", headers=HEADERS, proxies=PROXIES, timeout=10)
    print(f"✅ /user: {response.status_code}")
    if response.status_code != 404:
        print(f"📄 Body: {response.text[:100]}...")
except Exception as e:
    print(f"❌ /user error: {e}")

# Approach 4: Check if we need different headers
print(f"\n📡 Approach 4: Try with different headers")
try:
    alt_headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE}/auth/login", json={"test": "data"}, headers=alt_headers, proxies=PROXIES, timeout=10)
    print(f"✅ Bearer auth: {response.status_code}")
    if response.status_code != 404:
        print(f"📄 Body: {response.text[:100]}...")
except Exception as e:
    print(f"❌ Bearer auth error: {e}")

# Wait between requests
import time
time.sleep(2)
