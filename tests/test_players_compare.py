from orchestrator.tools import _per90

def test_per90_math():
    """Test per-90 calculations"""
    assert _per90(10, 1800) == 0.5
    assert _per90(0, 900) == 0.0
    assert _per90(5, 0) is None
    assert _per90(15, 2700) == 0.5
    assert _per90(1, 90) == 1.0

def test_per90_edge_cases():
    """Test edge cases for per-90 calculations"""
    assert _per90(None, 90) is None
    assert _per90(1, None) is None
    assert _per90(0, 90) == 0.0
    assert _per90(1, 45) == 2.0
