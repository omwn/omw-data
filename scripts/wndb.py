"""
Module for reading WNDB databases.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple, TextIO


# see: https://wordnet.princeton.edu/documentation/wninput5wn
POINTER_MAP = {
    "!": "antonym",
    "@": "hypernym",
    "@i": "instance_hypernym",
    "~": "hyponym",
    "~i": "instance_hyponym",
    "#m": "holo_member",
    "#s": "holo_substance",
    "#p": "holo_part",
    "%m": "mero_member",
    "%s": "mero_substance",
    "%p": "mero_part",
    "=": "attribute",
    "+": "derivation",
    ";c": "domain_topic",
    "-c": "has_domain_topic",
    ";r": "domain_region",
    "-r": "has_domain_region",
    ";u": "is_exemplified_by",  # was: domain usage
    "-u": "exemplifies",  # was: in domain usage
    "*": "entails",
    ">": "causes",
    "^": "also",
    "$": "similar",  # was: verb group
    "&": "similar",
    "<": "participle",
    "\\": "pertainym",
}

VERB_FRAMES = [
    (1, "Something ----s"),
    (2, "Somebody ----s"),
    (3, "It is ----ing"),
    (4, "Something is ----ing PP"),
    (5, "Something ----s something Adjective/Noun"),
    (6, "Something ----s Adjective/Noun"),
    (7, "Somebody ----s Adjective"),
    (8, "Somebody ----s something"),
    (9, "Somebody ----s somebody"),
    (10, "Something ----s somebody"),
    (11, "Something ----s something"),
    (12, "Something ----s to somebody"),
    (13, "Somebody ----s on something"),
    (14, "Somebody ----s somebody something"),
    (15, "Somebody ----s something to somebody"),
    (16, "Somebody ----s something from somebody"),
    (17, "Somebody ----s somebody with something"),
    (18, "Somebody ----s somebody of something"),
    (19, "Somebody ----s something on somebody"),
    (20, "Somebody ----s somebody PP"),
    (21, "Somebody ----s something PP"),
    (22, "Somebody ----s PP"),
    (23, "Somebody's (body part) ----s"),
    (24, "Somebody ----s somebody to INFINITIVE"),
    (25, "Somebody ----s somebody INFINITIVE"),
    (26, "Somebody ----s that CLAUSE"),
    (27, "Somebody ----s to somebody"),
    (28, "Somebody ----s to INFINITIVE"),
    (29, "Somebody ----s whether INFINITIVE"),
    (30, "Somebody ----s somebody into V-ing something"),
    (31, "Somebody ----s something with something"),
    (32, "Somebody ----s INFINITIVE"),
    (33, "Somebody ----s VERB-ing"),
    (34, "It ----s that CLAUSE"),
    (35, "Something ----s INFINITIVE"),
]

LEXICOGRAPHER_FILES = {
    "adj.all",
    "adj.pert",
    "adv.all",
    "noun.Tops",
    "noun.act",
    "noun.animal",
    "noun.artifact",
    "noun.attribute",
    "noun.body",
    "noun.cognition",
    "noun.communication",
    "noun.event",
    "noun.feeling",
    "noun.food",
    "noun.group",
    "noun.location",
    "noun.motive",
    "noun.object",
    "noun.person",
    "noun.phenomenon",
    "noun.plant",
    "noun.possession",
    "noun.process",
    "noun.quantity",
    "noun.relation",
    "noun.shape",
    "noun.state",
    "noun.substance",
    "noun.time",
    "verb.body",
    "verb.change",
    "verb.cognition",
    "verb.communication",
    "verb.competition",
    "verb.consumption",
    "verb.contact",
    "verb.creation",
    "verb.emotion",
    "verb.motion",
    "verb.perception",
    "verb.possession",
    "verb.social",
    "verb.stative",
    "verb.weather",
    "adj.ppl",
}

POS_MAP = {
    "n": "noun",
    "v": "verb",
    "a": "adj",
    "r": "adv",
}

SS_TYPE_MAP = {
    1: "n",
    2: "v",
    3: "a",
    4: "r",
    5: "s",
}

# Data and Data Types ##################################################


class WNDBError(Exception):
    """Raised on invalid WNDB databases."""


class Word(NamedTuple):
    word: str
    lex_id: int
    adjposition: str = ''

    @property
    def respaced(self) -> str:
        return self.word.replace("_", " ")

    @property
    def lemma(self) -> str:
        return self.word.lower()


class Pointer(NamedTuple):
    pointer_symbol: str
    synset_offset: int
    pos: str
    source_w_num: int
    target_w_num: int


class Frame(NamedTuple):
    f_num: int
    w_num: int


class DataRecord(NamedTuple):
    synset_offset: int
    lex_filenum: int
    ss_type: str
    words: list[Word]
    pointers: list[Pointer]
    frames: list[Frame]
    gloss: str


class IndexRecord(NamedTuple):
    lemma: str
    pos: str
    pointer_symbols: list[str]
    tagsense_cnt: int
    synset_offsets: list[int]


class Count(NamedTuple):
    tag_cnt: int
    sense_key: str
    sense_number: int


class SenseInfo(NamedTuple):
    sense_key: str
    synset_offset: int
    sense_number: int
    tag_cnt: int


class SenseKeyComponents(NamedTuple):
    lemma: str
    ss_type_idx: int
    lex_filenum: int
    lex_id: int
    head_word: str
    head_id: int

    @property
    def ss_type(self) -> str:
        return SS_TYPE_MAP[self.ss_type_idx]


class ExceptionalForm(NamedTuple):
    form: str
    base_forms: list[str]


# File reading #########################################################


def read_data_file(path: Path) -> Iterator[DataRecord]:
    """Yield DataRecords from a WNDB data file.

    After the header, the fields are:

        synset_offset  lex_filenum  ss_type
        w_cnt  word  lex_id  [word  lex_id...]
        p_cnt  [ptr...]
        [frames...]  |  gloss
    """
    with path.open("rt") as datafile:
        for line in _non_header_lines(datafile):
            nongloss, _, gloss = line.partition("|")
            synset_offset, lex_filenum, ss_type, _w_cnt, *rest = nongloss.strip().split(" ")

            w_cnt = int(_w_cnt, 16)  # word count is hexadecimal
            w_idx = w_cnt * 2  # each w is 2 columns: word, lex_id
            p_cnt = int(rest[w_idx])  # pointer count is decimal
            p_idx = w_idx + 1 + (p_cnt * 4)  # 4 cols: sym, offset, pos, src_tgt
            if len(rest) > p_idx and rest[p_idx]:
                f_cnt = int(rest[p_idx])  # frame count is decimal
            else:
                f_cnt = 0

            yield DataRecord(
                int(synset_offset),
                int(lex_filenum),
                ss_type,
                _parse_data_words(ss_type, rest[:w_idx], w_cnt),
                _parse_data_pointers(rest[w_idx + 1 : p_idx], p_cnt),
                _parse_data_frames(rest[p_idx + 1 :], f_cnt),
                gloss,
            )


def read_index_file(path: Path) -> Iterator[IndexRecord]:
    """Yield IndexRecords from a WNDB index file.

    After the header, the fields are:

        lemma  pos  synset_cnt  p_cnt  [ptr_symbol...]
        sense_cnt  tagsense_cnt   synset_offset  [synset_offset...]
    """
    with path.open("rt") as indexfile:
        for line in _non_header_lines(indexfile):
            lemma, pos, synset_cnt, _p_cnt, *rest = line.split()
            p_cnt = int(_p_cnt)
            p_symbols = rest[:p_cnt]
            _sense_cnt, *end = rest[p_cnt:]
            sense_cnt, end_cnt = int(_sense_cnt), len(end)
            if end_cnt == sense_cnt + 1:  # WN 1.6+
                tagsense_cnt, *offsets = end
            elif end_cnt == sense_cnt:  # WN 1.5
                tagsense_cnt, offsets = "0", end
            else:
                raise WNDBError(
                    f"Index entry {lemma!r} ({pos}) "
                    f"has {len(offsets)} offsets, "
                    f"expected {sense_cnt}"
                )
            yield IndexRecord(
                lemma,
                pos,
                p_symbols,
                int(tagsense_cnt),
                [int(offset) for offset in offsets],
            )


def read_count_list(path: Path) -> Iterator[Count]:
    """Yield Counts from a WNDB cntlist file.

    The fields are:

        tag_cnt  sense_key  sense_number
    """
    with path.open("rt") as cntlistfile:
        for line in _non_header_lines(cntlistfile):
            tag_cnt, sense_key, sense_number = line.split()
            yield Count(
                int(tag_cnt),
                sense_key,
                int(sense_number),
            )


def read_sense_index(path: Path) -> Iterator[SenseInfo]:
    """Yield SenseInfos from a WNDB senseidx file.

    The fields are:

        sense_key  synset_offset  sense_number  tag_cnt
    """
    with path.open("rt") as senseindexfile:
        for line in _non_header_lines(senseindexfile):
            sense_key, offset, sense_number, *extra = line.split()
            # 0 is a valid count, so use -1 if the count field is missing
            tag_cnt = int(extra[0]) if extra else -1
            yield SenseInfo(
                sense_key,
                int(offset),
                int(sense_number),
                tag_cnt,
            )


def read_exceptions_file(path: Path) -> Iterator[ExceptionalForm]:
    """Yield ExceptionalForms from a WNDB exception list file.

    The fields are:

        inflected_form base_form [base_form...]
    """
    with path.open("rt") as exceptionfile:
        for line in exceptionfile:
            form, *bases = line.split()
            yield ExceptionalForm(form, bases)


# Data field parsing ###################################################


def _parse_data_words(
    ss_type: str,
    xs: list[str],
    w_cnt: int,
) -> list[Word]:
    words = []
    for lemma, lex_id in zip(xs[::2], xs[1::2]):
        lemma, adjposition = _split_adjposition(lemma, ss_type)
        words.append(Word(lemma, int(lex_id, 16), adjposition))
    assert len(words) == w_cnt, f"{len(words)=} {w_cnt=}"
    return words


def _split_adjposition(lemma: str, ss_type: str) -> tuple[str, str]:
    if ss_type in "as" and lemma.endswith(")"):
        if lemma.endswith("(a)"):
            return lemma[:-3], "a"
        elif lemma.endswith("(p)"):
            return lemma[:-3], "p"
        elif lemma.endswith("(ip)"):
            return lemma[:-4], "ip"
    return lemma, ''


def _parse_data_pointers(xs: list[str], p_cnt: int) -> list[Pointer]:
    pointers = []
    for sym, offset, pos, src_tgt in zip(xs[::4], xs[1::4], xs[2::4], xs[3::4]):
        src, tgt = src_tgt[:2], src_tgt[2:]
        pointers.append(Pointer(sym, int(offset), pos, int(src, 16), int(tgt, 16)))
    assert len(pointers) == p_cnt, f"{len(pointers)=} {p_cnt=}"
    return pointers


def _parse_data_frames(xs: list[str], f_cnt: int) -> list[Frame]:
    frames = []
    for _, f_num, w_num in zip(xs[::3], xs[1::3], xs[2::3]):
        frames.append(Frame(int(f_num), int(w_num, 16)))
    assert len(frames) == f_cnt
    return frames


# Sense Keys ###########################################################

def sense_key_lemma(sense_key: str) -> str:
    return sense_key.rpartition("%")[0]


def split_sense_key(sense_key: str) -> SenseKeyComponents:
    lemma, _, rest = sense_key.rpartition("%")
    ss_type_idx, lex_filenum, lex_id, head_word, head_id = rest.split(":")
    return SenseKeyComponents(
        lemma,
        int(ss_type_idx),
        int(lex_filenum),
        int(lex_id),
        head_word,
        int(head_id) if head_id else 0,
    )


# Helper functions #####################################################


def _non_header_lines(file: TextIO) -> Iterator[str]:
    try:
        line = next(file)
        while _is_header_line(line):
            line = next(file)
        # done with header
        yield line
        yield from file
    except StopIteration:
        pass


def _is_header_line(line: str) -> bool:
    return line.startswith("  ") or line.strip() in LEXICOGRAPHER_FILES
