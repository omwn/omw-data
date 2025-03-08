from scripts import tsv2lmf


def test_load(datadir):
    data = tsv2lmf.load(datadir / "test.tab", "omw-tst")
    assert data.label == "Test Wordnet"
    assert data.language == "tst"
    assert data.url == "http://www.globalwordnet.org/test/"
    assert data.license == "CC BY 4.0"

    assert len(data.synsets) == 4
    assert len(data.entries) == 5

    foo_n = data.entries["omw-tst-foo-n"]
    assert foo_n.pos == "n"
    assert len(foo_n.senses) == 2
    foo_00001234_n = foo_n.senses["00001234-n"]
    assert len(foo_00001234_n["counts"]) == 1
    assert foo_00001234_n["counts"][0]["value"] == 2

    n_00001234 = data.synsets["00001234-n"]
    assert len(n_00001234.members) == 2
    assert n_00001234.definitions == [(0, "a bar that foos")]

    assert foo_n.senses["00001234-n"] is n_00001234.members["foo"]

    assert data.entries["omw-tst-fooey-a"].pos == "a"
    assert data.synsets["00003456-s"].pos == "a"

    bar_n = data.entries["omw-tst-bar-n"]
    assert len(bar_n.forms[0]["pronunciations"]) == 1
    assert bar_n.forms[0]["pronunciations"][0]["audio"] == "https://example.com/bar.mp3"
