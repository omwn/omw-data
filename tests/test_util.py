from scripts.util import escape_lemma

def test_escape_lemma():
    assert escape_lemma("abc") == "abc"
    assert escape_lemma("a.b.c") == "a.b.c"
    assert escape_lemma("protégé") == "protégé"
    assert escape_lemma("a b c") == "a_b_c"
    assert escape_lemma("a:b:c") == "a-colon-b-colon-c"
    assert escape_lemma("a-b-c") == "a--b--c"
    assert escape_lemma("a´b´c") == "a-acute-b-acute-c"
    assert escape_lemma("a_b_c") == "a-lowbar-b-lowbar-c"
