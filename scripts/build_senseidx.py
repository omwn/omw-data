"""
Build senseidx (index.sense) from WNDB

Usage example:

$ python -m scripts.build_senseidx \
         WordNet-3.0/dict/ \
         --outfile index.sense

Requirements:

- The Wn Python library: https://github.com/goodmami/wn
- The Pe Python library: https://github.com/goodmami/pe
- WNDB source files: https://wordnet.princeton.edu/download

This script builds the senseidx (filename: index.sense) file from a
WNDB database. In order to do so, it combines information from the
data files, index files, and countlists.

The senseidx format and file contents are described in the Princeton
WordNet documentation:
https://wordnet.princeton.edu/documentation/senseidx5wn

Author: Michael Wayne Goodman (https://github.com/goodmami)
License: MIT
"""

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple, TextIO

from .wndb import (
    SenseInfo,
    Word,
    read_count_list,
    read_data_file,
    read_index_file,
)


REV_SS_TYPE_MAP = {
    "n": 1,
    "v": 2,
    "a": 3,
    "r": 4,
    "s": 5,
}
DEFAULT_HEAD_WORD = Word("", 0, None)  # for synsets that aren't satellite adjectives

SensenumMap = dict[tuple[str, int], int]  # maps (lemma, synset_offset) to a sensenum


class RawSenseInfo(NamedTuple):
    """Raw data used to construct SenseInfo object."""

    lemma: str
    ss_type: str
    lex_filenum: int
    lex_id: int
    head_lemma: str
    head_adjposition: str
    head_lex_id: int
    synset_offset: int
    sense_number: int


def main(args: argparse.Namespace) -> None:
    path = Path(args.WNDBPATH)
    if not path.is_dir():
        sys.exit(f"Not a directory: {path!s}")

    data = list(prepare_raw_senseinfo(path, "noun"))
    data.extend(prepare_raw_senseinfo(path, "verb"))
    data.extend(prepare_raw_senseinfo(path, "adj"))
    data.extend(prepare_raw_senseinfo(path, "adv"))

    senseidx = build_senseidx(
        data,
        make_count_map(path),
        args.use_adjposition,
    )

    if args.outfile == "-":
        dump(senseidx, sys.stdout)
    else:
        with open(args.outfile, "wt", encoding="utf-8") as outfile:
            dump(senseidx, outfile)


def prepare_raw_senseinfo(path: Path, suffix: str) -> Iterator[RawSenseInfo]:
    sensenum_map = make_sensenum_map(path / f"index.{suffix}")
    data_map = {dr.synset_offset: dr for dr in read_data_file(path / f"data.{suffix}")}

    for dr in data_map.values():
        members: set[str] = set()
        head_word = find_adj_satellite_head(dr, data_map)

        for word in dr.words:
            lemma = word.lemma
            sense_number = sensenum_map[(lemma, dr.synset_offset)]

            if lemma in members:  # ignore small differences like "A.M." vs "a.m."
                continue
            members.add(lemma)

            yield RawSenseInfo(
                lemma=lemma,
                ss_type=dr.ss_type,
                lex_filenum=dr.lex_filenum,
                lex_id=word.lex_id,
                head_lemma=head_word.lemma,
                head_adjposition=head_word.adjposition,
                head_lex_id=head_word.lex_id,
                synset_offset=dr.synset_offset,
                sense_number=sense_number,
            )


def make_sensenum_map(path: Path) -> SensenumMap:
    return {
        (ir.lemma, synset_offset): sense_num
        for ir in read_index_file(path)
        for sense_num, synset_offset in enumerate(ir.synset_offsets, 1)
    }


def build_senseidx(
    data: list[RawSenseInfo],
    countmap: dict[str, int],
    use_adjposition: bool,
) -> list[SenseInfo]:
    senseidx: list[SenseInfo] = []
    for raw_senseinfo in sorted(data):
        sense_key = make_sense_key(raw_senseinfo, use_adjposition)
        count = countmap.get(normalize_sense_key(sense_key), 0)
        senseidx.append(
            SenseInfo(
                sense_key,
                raw_senseinfo.synset_offset,
                raw_senseinfo.sense_number,
                count,
            )
        )
    return senseidx


def make_count_map(path: Path) -> dict[str, int]:
    return {
        normalize_sense_key(count.sense_key): count.tag_cnt
        for count in read_count_list(path / "cntlist")
    }


def find_adj_satellite_head(record, data_map) -> Word:
    if record.ss_type != "s":
        return DEFAULT_HEAD_WORD
    similar_to, *extra = (ptr for ptr in record.pointers if ptr.pointer_symbol == "&")
    if extra:
        pass  # warn?
    assert similar_to.target_w_num == 0  # semantic relation only
    head_record = data_map[similar_to.synset_offset]
    return head_record.words[0]  # first word of the satellite's head


def normalize_sense_key(sense_key: str) -> str:
    key, _, head_id = sense_key.rpartition(":")
    key = key.removesuffix("(a)").removesuffix("(p)").removesuffix("(ip)")
    return f"{key}:{head_id}"


def make_sense_key(
    rsi: RawSenseInfo,
    use_adjposition: bool,
) -> str:
    if use_adjposition and rsi.head_adjposition:
        head_word = f"{rsi.head_lemma}({rsi.head_adjposition})"
    else:
        head_word = rsi.head_lemma
    return format_sense_key(
        rsi.lemma,
        REV_SS_TYPE_MAP[rsi.ss_type],
        rsi.lex_filenum,
        rsi.lex_id,
        head_word,
        rsi.head_lex_id,
    )


def format_sense_key(
    lemma: str,
    ss_type_idx: int,
    lex_filenum: int,
    lex_id: int,
    head_word: str = "",
    head_id: int = 0,
) -> str:
    h_id = f"{head_id:02}" if head_word else ""
    return f"{lemma}%{ss_type_idx}:{lex_filenum:02}:{lex_id:02}:{head_word}:{h_id}"


def dump(senseidx: list[SenseInfo], file: TextIO) -> None:
    for si in sorted(senseidx):
        print(
            f"{si.sense_key} {si.synset_offset:08} {si.sense_number} {si.tag_cnt}",
            file=file,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Build a senseidx file from WNDB")
    parser.add_argument("WNDBPATH", help="path to the WNDB directory")
    parser.add_argument(
        "-o",
        "--outfile",
        default="-",
        help="path to direct output (stdout if - or unused)",
    )
    parser.add_argument(
        "--use-adjposition",
        action="store_true",
        help="for compatibility, output adjpositions on satellite head words",
    )
    args = parser.parse_args()
    main(args)
