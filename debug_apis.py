#!/usr/bin/env python3
"""
Debug script to test football APIs and see what's happening
"""

import os
import asyncio
from dotenv import load_dotenv
from services.football_api import FootballAPIService

async def test_apis():
    """Test all football APIs and show results"""
    print("🔍 Testing Football APIs...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    football_data_key = os.getenv('FOOTBALL_DATA_API_KEY')
    api_football_key = os.getenv('API_FOOTBALL_KEY')
    
    print(f"🔑 Football-Data.org API Key: {'✅ Set' if football_data_key else '❌ Not Set'}")
    if football_data_key:
        print(f"   Key: {football_data_key[:10]}...{football_data_key[-4:]}")
    
    print(f"🔑 API-Football Key: {'✅ Set' if api_football_key else '❌ Not Set'}")
    if api_football_key:
        print(f"   Key: {api_football_key[:10]}...{api_football_key[-4:]}")
    
    print()
    
    # Initialize API service
    api_service = FootballAPIService()
    
    # Test Real Madrid info
    print("📊 Testing Real Madrid Info...")
    try:
        madrid_info = await api_service.get_real_madrid_info()
        print(f"✅ Success: {madrid_info.get('name', 'Unknown')}")
        print(f"   Source: {madrid_info.get('source', 'Unknown')}")
        print(f"   Stadium: {madrid_info.get('venue', 'Unknown')}")
        print(f"   Founded: {madrid_info.get('founded', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test squad
    print("👥 Testing Squad Data...")
    try:
        squad = await api_service.get_real_madrid_squad()
        print(f"✅ Success: {len(squad)} players")
        print(f"   Source: {squad[0].get('source', 'Unknown') if squad else 'None'}")
        if squad:
            print(f"   Sample players: {[p.get('name', 'Unknown') for p in squad[:3]]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test matches
    print("⚽ Testing Match Data...")
    try:
        matches = await api_service.get_real_madrid_matches(limit=3)
        print(f"✅ Success: {len(matches)} matches")
        print(f"   Source: {matches[0].get('source', 'Unknown') if matches else 'None'}")
        if matches:
            for i, match in enumerate(matches[:2]):
                print(f"   Match {i+1}: {match.get('home_team')} vs {match.get('away_team')} ({match.get('competition')})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test standings
    print("🏆 Testing Standings Data...")
    try:
        standings = await api_service.get_la_liga_standings()
        print(f"✅ Success: {len(standings)} teams")
        print(f"   Source: {standings[0].get('source', 'Unknown') if standings else 'None'}")
        if standings:
            top_3 = [f"{s.get('position')}. {s.get('team')}" for s in standings[:3]]
            print(f"   Top 3: {top_3}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 50)
    print("🎯 Debug Complete!")

if __name__ == "__main__":
    asyncio.run(test_apis())
