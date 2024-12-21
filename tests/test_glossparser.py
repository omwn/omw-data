from scripts.glossparser import gloss_parser

groups = lambda s: gloss_parser.match(s).groups()

def test_empty():
    assert groups("") == ("", [])
    assert groups(" ") == ("", [])


def test_definition_only():
    assert groups("A definition") == ("A definition", [])
    # don't split multiple definitions
    assert groups("First definition; Second definition") == (
        "First definition; Second definition", []
    )


def test_delimiter():
    assert groups('def; "ex"') == ("def", ['"ex"'])
    assert groups('def: "ex"') == ("def", ['"ex"'])
    assert groups('def, "ex"') == ("def", ['"ex"'])


def test_definition_with_quotes():
    assert groups('Defined as "word"') == ('Defined as "word"', [])
    assert groups('Defined as "word"; "ex"') == ('Defined as "word"', ['"ex"'])
    assert groups('A "word" or some other "word"') == (
        'A "word" or some other "word"', []
    )

def test_definition_with_quote_characters():
    assert groups('some definition"') == ('some definition"', [])
    assert groups('some definition"; "ex"') == ('some definition"', ['"ex"'])
    assert groups('some definition" "ex"') == ('some definition"', ['"ex"'])
    assert groups('some 1" definition; "ex"') == ('some 1" definition', ['"ex"'])

def test_definition_with_parentheses():
    assert groups('(informal) a definition') == ('(informal) a definition', [])
    assert groups('something (or: "other"); "ex"') == (
        'something (or: "other")', ['"ex"']
    )


def test_definition_with_eg():
    assert groups('definition: e.g., "word"; "ex"') == (
        'definition: e.g., "word"', ['"ex"']
    )
    assert groups('eg "word"') == ('eg "word"', [])


def test_examples_only():
    assert groups('"example"') == ("", ['"example"'])
    assert groups('"ex1"; "ex2"') == ("", ['"ex1"', '"ex2"'])


def test_examples_dialogue():
    assert groups('definition; "Hi," they said') == (
        "definition", ['"Hi," they said']
    )
    assert groups('"What," she asked, "is that?"; "Ask again"') == (
        "", ['"What," she asked, "is that?"', '"Ask again"']
    )


def test_examples_extra_quotes():
    assert groups('definition: ""word"; "again""') == (
        "definition", ['""word"', '"again""']
    )
    assert groups('definition: "word""; ""again"') == (
        "definition", ['"word""', '""again"']
    )
    assert groups('def: "word" is a word"') == (
        "def", ['"word" is a word"']
    )


def test_examples_missing_final_quote():
    assert groups('def; "example') == ("def", ['"example'])


def test_examples_without_delimiter():
    assert groups('def; "ex1""ex2"') == ("def", ['"ex1"', '"ex2"'])
    assert groups('def; "ex1" "ex2"') == ("def", ['"ex1"', '"ex2"'])
    assert groups('def; "ex1"; "ex2" "ex3"') == ("def", ['"ex1"', '"ex2"', '"ex3"'])


# Not doing this now
# def test_examples_alpha_delimiters():
#     assert groups('def; "ex1" or "ex2"') == ("def", ['"ex1"', '"ex2"'])
#     assert groups('def; "ex1" for "ex2"') == ("def", ['"ex1" for "ex2"'])
#     assert groups('def; "ex1a" vs "ex1b" or "ex2"') == ("def", ['"ex1a" vs "ex1b"', '"ex2"'])
#     assert groups('def; "ex1a" vs "ex1b" or "ex2a" vs "ex2b"') == (
#         "def", ['"ex1a" vs "ex1b"', '"ex2a" vs "ex2b"']
#     )


def test_examples_author():
    assert groups('def; "ex1" - an author') == ("def", ['"ex1" - an author'])
    assert groups('def; "ex2"; "ex1" - an author') == (
        "def", ['"ex2"', '"ex1" - an author']
    )
