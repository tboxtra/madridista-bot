#!/usr/bin/env python3
"""
Test script to debug live API calls and see exactly what's happening
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def test_football_data_api():
    """Test Football-Data.org API directly"""
    print("🔍 Testing Football-Data.org API directly...")
    
    load_dotenv()
    api_key = os.getenv('FOOTBALL_DATA_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test Real Madrid team info
    url = "http://api.football-data.org/v4/teams/86"
    headers = {'X-Auth-Token': api_key}
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🌐 Making request to: {url}")
            async with session.get(url, headers=headers) as response:
                print(f"📡 Response status: {response.status}")
                print(f"📡 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success! Team: {data.get('name', 'Unknown')}")
                    print(f"   Founded: {data.get('founded', 'Unknown')}")
                    print(f"   Venue: {data.get('venue', 'Unknown')}")
                    print(f"   Squad size: {len(data.get('squad', []))}")
                else:
                    error_text = await response.text()
                    print(f"❌ Error response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_api_football():
    """Test API-Football directly"""
    print("\n🔍 Testing API-Football directly...")
    
    load_dotenv()
    api_key = os.getenv('API_FOOTBALL_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test a simple endpoint
    url = "https://v3.football.api-sports.io/status"
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🌐 Making request to: {url}")
            async with session.get(url, headers=headers) as response:
                print(f"📡 Response status: {response.status}")
                print(f"📡 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success! API status: {data}")
                else:
                    error_text = await response.text()
                    print(f"❌ Error response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_our_service():
    """Test our FootballAPIService"""
    print("\n🔍 Testing our FootballAPIService...")
    
    try:
        from services.football_api import FootballAPIService
        
        service = FootballAPIService()
        
        # Test Real Madrid info
        print("📊 Testing get_real_madrid_info...")
        info = await service.get_real_madrid_info()
        print(f"   Result: {info.get('name', 'Unknown')}")
        print(f"   Source: {info.get('source', 'Unknown')}")
        
        # Test squad
        print("👥 Testing get_real_madrid_squad...")
        squad = await service.get_real_madrid_squad()
        print(f"   Result: {len(squad)} players")
        if squad:
            print(f"   Source: {squad[0].get('source', 'Unknown')}")
            print(f"   Sample: {[p.get('name', 'Unknown') for p in squad[:3]]}")
        
        # Test matches
        print("⚽ Testing get_real_madrid_matches...")
        matches = await service.get_real_madrid_matches(limit=2)
        print(f"   Result: {len(matches)} matches")
        if matches:
            print(f"   Source: {matches[0].get('source', 'Unknown')}")
            for match in matches:
                print(f"   Match: {match.get('home_team')} vs {match.get('away_team')}")
        
    except Exception as e:
        print(f"❌ Exception in our service: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("🧪 Comprehensive API Testing")
    print("=" * 50)
    
    await test_football_data_api()
    await test_api_football()
    await test_our_service()
    
    print("\n" + "=" * 50)
    print("🎯 Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())
