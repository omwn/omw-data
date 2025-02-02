import csv
import warnings
from html.entities import codepoint2name
from pathlib import Path
from typing import NamedTuple, Union

PathLike = Union[str, Path]


_custom_char_escapes = {
    # HTML entities not included in codepoint2name
    # https://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references
    ' ': '_',            # custom
    '!': '-excl-',
    '#': '-num-',
    '$': '-dollar-',
    '%': '-percnt-',
    "'": '-apos-',
    '(': '-lpar-',
    ')': '-rpar-',
    '*': '-ast-',
    '+': '-plus-',
    ',': '-comma-',
    '-': '--',           # custom
    '.': '.',            # keep
    '/': '-sol-',
    ':': '-colon-',
    ';': '-semi-',
    '=': '-equals-',
    '?': '-quest-',
    '@': '-commat-',
    '[': '-lsqb-',
    '\\': '-bsol-',
    ']': '-rsqb-',
    '^': '-Hat-',
    '_': '-lowbar-',
    '`': '-grave-',
    '{': '-lbrace-',
    '|': '-vert-',
    '}': '-rbrace-',
}


def escape_lemma(lemma: str) -> str:
    chars = []
    for c in lemma:
        codepoint = ord(c)
        if ('A' <= c <= 'Z'
                or 'a' <= c <= 'z'
                or '0' <= c <= '9'  # not in initial position
                # or c == ':'  # drop this for xsd:id compatibility
                # or c in '-'  # blocked for special purpose (see below)
                or c in '.·'
                or 0xC0 <= codepoint <= 0xD6
                or 0xD8 <= codepoint <= 0xF6
                or 0xF8 <= codepoint <= 0x2FF
                or 0x300 <= codepoint <= 0x36F  # not in initial position
                or 0x370 <= codepoint <= 0x37D
                or 0x37F <= codepoint <= 0x1FFF
                or codepoint in (0x200C, 0x200D,
                                 0x203F, 0x2040)  # these two not in initial position
                or 0x2C00 <= codepoint <= 0x2FEF
                or 0x3001 <= codepoint <= 0xD7FF
                or 0xF900 <= codepoint <= 0xFDCF
                or 0xFDF0 <= codepoint <= 0xFFFD
                or 0x10000 <= codepoint <= 0xEFFFF):
            # acceptable character
            chars.append(c)
        elif c in _custom_char_escapes:
            chars.append(_custom_char_escapes[c])
        elif codepoint in codepoint2name:
            chars.append(f"-{codepoint2name[codepoint]}-")
        else:
            esc = f'-{codepoint:04X}-'
            warnings.warn(f'no escape character defined for {c!r}; using {esc}')
            chars.append(esc)
    return ''.join(chars)


def despace_word(word: str) -> str:
    """Replace spaces with _ as in WNDB data files."""
    return word.replace(" ", "_")


def respace_word(word: str) -> str:
    """Replace _ with spaces."""
    return word.replace("_", " ")


def format_lemma(word: str) -> str:
    """Format a word as a lemma in a WNDB index file."""
    return despace_word(word).lower()


def load_ili_map(path) -> dict[str, str]:
    ilimap = {}
    with open(path, 'rt') as ilifile:
        for line in ilifile:
            ili, ssid = line.strip().split('\t')
            ilimap[ssid] = ili
            if ssid.endswith('-s'):
                ilimap[ssid[:-2] + '-a'] = ili  # map as either -s or -a
    return ilimap


class TSVRow(NamedTuple):
    offset_pos: str
    type: str
    text: str
    order: int = -1  # only used by def and exe

    def is_lemma(self) -> bool:
        """Return True if the row is a lemma row.

        Usually the row type is of the form `xyz:lemma` where `xyz` is
        the language code. There are variations like `xyz:lemma:root`
        and `xyz:lemma:brokenplural` (currently only in the Arabic
        wordnet) or just `lemma`.
        """
        return "lemma" in self.type


def load_tsv(path: PathLike) -> tuple[str, list[TSVRow]]:
    with Path(path).open(newline='') as csvfile:
        reader = csv.reader(csvfile, dialect='excel-tab', quoting=csv.QUOTE_NONE)
        header = "\t".join(next(reader))
        rows: list[TSVRow] = []
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            if "lemma" in row[1]:
                assert len(row) == 3, f"unexpected number of columns for lemma: {row}"
                rows.append(TSVRow(*row[:3]))
            elif row[1].endswith((":def", ":exe")):
                assert len(row) == 4, f"unexpected number of columns for def/exe: {row}"
                rows.append(TSVRow(*row[:2], row[3], order=row[2]))
            else:
                raise Exception(f"unexpected row: {row}")
    return header, rows


QUOTES = [
    ('"', '"'),
    ("'", "'"),
    ("`", "'"),
    ("``", "''"),
    ("„", "“"),
    ("„", "”"),
    ("‚", "’"),
    ("‚", "‘"),
    ("»", "«"),
    ("«", "»"),
    ("’", "’"),
    ("‚", "‚"),
    ('“', '”'),
    ("‘", "’"),
    ("”", "”"),
    ("»", "«"),
    ("‹", "›"),
    ("《", "》"),
    ("【", "】"),
    #("<", ">"),
    ("「", "」"),
    ("『", "』"),
    ("〈", "〉"),
    ("〖", "〗"),
]


def strip_quotes(lemma: str) -> str:
    for start, end in QUOTES:
        if lemma.startswith(start) and lemma.endswith(end):
            return lemma.removeprefix(start).removesuffix(end).strip()
    return lemma
