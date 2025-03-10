from scripts import tsv2lmf


def test_load_header(datadir):
    data = tsv2lmf.load(datadir / "test.tab", "omw-tst")
    assert data.label == "Test Wordnet"
    assert data.language == "tst"
    assert data.url == "http://www.globalwordnet.org/test/"
    assert data.license == "CC BY 4.0"

def test_load_basic(datadir):
    data = tsv2lmf.load(datadir / "test.tab", "omw-tst")
    assert len(data.synsets) == 4
    assert len(data.entries) == 5

    foo_n = data.entries["omw-tst-foo-n"]
    assert foo_n.pos == "n"
    assert len(foo_n.senses) == 2

    n_00001234 = data.synsets["00001234-n"]
    assert len(n_00001234.members) == 2
    assert n_00001234.definitions == [(0, "a bar that foos")]

    n_00002345 = data.synsets["00002345-n"]
    assert len(n_00002345.members) == 2
    assert n_00002345.examples == [(1, "I have a baz"), (0, "I have a foo")]

    assert data.entries["omw-tst-fooey-a"].pos == "a"
    assert data.synsets["00003456-s"].pos == "a"


def test_load_count(datadir):
    data = tsv2lmf.load(datadir / "test-count.tab", "omw-tst")
    n_00001234 = data.synsets["00001234-n"]

    foo_00001234_n = n_00001234.members["foo"]
    assert len(foo_00001234_n["counts"]) == 1
    assert foo_00001234_n["counts"][0]["value"] == 2

    bar_00001234_n = n_00001234.members["bar"]
    assert len(bar_00001234_n["counts"]) == 1
    assert bar_00001234_n["counts"][0]["value"] == 4


def test_load_pron(datadir):
    data = tsv2lmf.load(datadir / "test-pron.tab", "omw-tst")
    foo_n_0 = data.entries["omw-tst-foo-n"].forms[0]
    assert len(foo_n_0["pronunciations"]) == 0

    bar_n_0 = data.entries["omw-tst-bar-n"].forms[0]
    assert len(bar_n_0["pronunciations"]) == 1
    assert bar_n_0["pronunciations"][0]["audio"] == "https://example.com/bar.mp3"


def test_load_wordforms(datadir):
    data = tsv2lmf.load(datadir / "test-wordforms.tab", "omw-tst")
    kitab_n = data.entries["omw-tst-kitab-n"]
    assert len(kitab_n.forms) == 3

    kitab_n_0 = kitab_n.forms[0]
    assert kitab_n_0["writtenForm"] == "kitab"
    assert kitab_n.forms[0].get("tags", []) == []

    kitab_n_1 = kitab_n.forms[1]
    assert kitab_n_1["writtenForm"] == "ktb"
    assert kitab_n_1["tags"][0]["category"] == "form"
    assert kitab_n_1["tags"][0]["text"] == "root"

    kitab_n_2 = kitab_n.forms[2]
    assert kitab_n_2["writtenForm"] == "kutub"
    assert kitab_n_2["tags"][0]["category"] == "number"
    assert kitab_n_2["tags"][0]["text"] == "plural"


def test_load_gap(datadir):
    data = tsv2lmf.load(datadir / "test-gap.tab", "omw-tst")

    n_00001234 = data.synsets["00001234-n"]
    n_00002345 = data.synsets["00002345-n"]
    s_00003456 = data.synsets["00003456-s"]

    assert all(sd.lexicalized for sd in [n_00001234, n_00002345, s_00003456])

    assert all(sense.get("lexicalized", True) for sense in n_00001234.members.values())
    assert all(sense.get("lexicalized", True) for sense in n_00002345.members.values())
    assert all(sense.get("lexicalized", True) for sense in s_00003456.members.values())

    assert "GAP!" in n_00001234.members
    assert "GAP!" in n_00002345.members
    assert "PSEUDOGAP!" in s_00003456.members

    tsv2lmf.process_lexical_gaps(data)

    assert n_00001234.lexicalized
    assert not n_00002345.lexicalized
    assert not s_00003456.lexicalized

    assert n_00001234.members["foo"].get("lexicalized", True)
    assert not n_00001234.members["a bar that foos"]["lexicalized"]
    assert len(n_00002345.members) == 0
    assert not s_00003456.members["very fooey"]["lexicalized"]
    assert not s_00003456.members["very barlike"]["lexicalized"]

    assert "GAP!" not in n_00001234.members
    assert "GAP!" not in n_00002345.members
    assert "PSEUDOGAP!" not in s_00003456.members
