
from typing import Dict
import warnings
from html.entities import codepoint2name

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
    '_': '_',            # keep, even though it's conflated with ' ' -> '_'
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
                or c in '_.·'  # _ is special-purpose, but accept
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
            chars.append(codepoint2name[codepoint])
        else:
            esc = f'-{codepoint:04X}-'
            warnings.warn(f'no escape character defined for {c!r}; using {esc}')
            chars.append(esc)
    return ''.join(chars)


def load_ili_map(path) -> Dict[str, str]:
    ilimap = {}
    with open(path, 'rt') as ilifile:
        for line in ilifile:
            ili, ssid = line.strip().split('\t')
            ilimap[ssid] = ili
            if ssid.endswith('-s'):
                ilimap[ssid[:-2] + '-a'] = ili  # map as either -s or -a
    return ilimap
