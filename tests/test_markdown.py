from utils.formatting import md_escape

def test_md_escape():
    s = "AC_Madrid*Pro [A] `code`"
    out = md_escape(s)
    for ch in ["*", "_", "`", "["]:
        assert ch not in out
