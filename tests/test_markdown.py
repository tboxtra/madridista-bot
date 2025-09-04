from utils.formatting import md_escape

def test_md_escape_removes_specials():
    s = "AC_Madrid*Pro [A] `code`"
    out = md_escape(s)
    for ch in ["*", "_", "`", "["]:
        assert ch not in out
