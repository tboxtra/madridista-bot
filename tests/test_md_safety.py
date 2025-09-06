from utils.formatting import md_escape

def test_md_escape_safe():
    """Test markdown escaping for Telegram safety"""
    s = "AC_Madrid*Pro [A] `x`"
    out = md_escape(s)
    
    # All markdown special characters should be escaped
    for ch in "_*[]`":
        assert ch not in out
    
    # Should contain backslashes for escaped characters
    assert "\\" in out

def test_md_escape_edge_cases():
    """Test edge cases for markdown escaping"""
    # Empty string
    assert md_escape("") == ""
    assert md_escape(None) == ""
    
    # String with no special characters
    assert md_escape("normal text") == "normal text"
    
    # String with all special characters
    s = "_*[]()~`>#+-=|{}.!"
    out = md_escape(s)
    # All characters should be escaped
    assert len(out) == len(s) * 2  # Each char becomes \char
