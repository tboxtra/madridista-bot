#!/usr/bin/env python3
"""
Check TwitterAPI.io overall API status
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

# Test different base URLs and simple endpoints
base_urls = [
    "https://api.twitterapi.io",
    "https://api.twitterapi.io/v1",
    "https://api.twitterapi.io/v2",
    "https://twitterapi.io/api",
    "https://twitterapi.io"
]

print(f"\n🚀 Checking API status across different base URLs...")

for base in base_urls:
    print(f"\n🌐 Testing base: {base}")
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base}/", headers={"x-api-key": API_KEY}, proxies={"http": PROXY_URL, "https": PROXY_URL}, timeout=10)
        print(f"  Root /: {response.status_code}")
        if response.status_code != 404:
            print(f"    📄 Body: {response.text[:100]}...")
    except Exception as e:
        print(f"  Root /: ❌ {e}")
    
    # Test 2: Health check endpoint
    try:
        response = requests.get(f"{base}/health", headers={"x-api-key": API_KEY}, proxies={"http": PROXY_URL, "https": PROXY_URL}, timeout=10)
        print(f"  Health /health: {response.status_code}")
        if response.status_code != 404:
            print(f"    📄 Body: {response.text[:100]}...")
    except Exception as e:
        print(f"  Health /health: ❌ {e}")
    
    # Test 3: Status endpoint
    try:
        response = requests.get(f"{base}/status", headers={"x-api-key": API_KEY}, proxies={"http": PROXY_URL, "https": PROXY_URL}, timeout=10)
        print(f"  Status /status: {response.status_code}")
        if response.status_code != 404:
            print(f"    📄 Body: {response.text[:100]}...")
    except Exception as e:
        print(f"  Status /status: ❌ {e}")
    
    # Wait between base URLs
    import time
    time.sleep(2)
