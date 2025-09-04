#!/usr/bin/env python3
"""
Ultra-fast MadridistaAI test - just run with TOTP code!
Usage: python3 quick_test.py <TOTP_CODE>
"""

import os, sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Check TOTP code
if len(sys.argv) < 2:
    print("❌ Usage: python3 quick_test.py <TOTP_CODE>")
    sys.exit(1)

TOTP_CODE = sys.argv[1]
print(f"🔐 Using TOTP: {TOTP_CODE}")

# Test TwitterAPI.io directly
import requests

API_KEY = os.getenv("TWITTERAPI_IO_KEY")
USERNAME = os.getenv("TW_USERNAME") 
PASSWORD = os.getenv("TW_PASSWORD")
PROXY_URL = os.getenv("PROXY_URL")

print(f"🔑 API Key: {API_KEY[:10]}...")
print(f"👤 Username: {USERNAME}")
print(f"🌐 Proxy: {PROXY_URL}")

# Test multiple endpoints
BASE = "https://api.twitterapi.io"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

endpoints_to_test = [
    "/auth/login",
    "/login", 
    "/twitter/login",
    "/user/login",
    "/api/login",
    "/v1/login",
    "/v2/login"
]

print(f"\n🚀 Testing multiple endpoints...")

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
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")
