from utils.timeutil import is_fresh_iso

def test_is_fresh_iso():
    """Test freshness validation"""
    # Recent date should be fresh
    assert is_fresh_iso("2025-01-20T20:00:00Z", days=30) is True
    
    # Old date should not be fresh
    assert is_fresh_iso("2024-01-01T00:00:00Z", days=120) is False
    
    # Edge case: exactly at the boundary
    assert is_fresh_iso("2024-09-20T20:00:00Z", days=120) is False
    
    # Invalid date should return False
    assert is_fresh_iso("invalid-date", days=30) is False
    assert is_fresh_iso("", days=30) is False
