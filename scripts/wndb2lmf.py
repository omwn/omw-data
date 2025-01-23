#!/usr/bin/env python3

"""WNDB to WN-LMF converter

Usage example:

$ python -m scripts.wndb2lmf.py \
         WordNet-3.0/dict/ \
         wn30.xml \
         --id='wn30' \
         --version='1.4' \
         --label='English Wordnet based on the Princeton WordNet 3.0' \
         --language='en' \
         --email='maintainer@example.com' \
         --license='https://...' \
         --ili-map=cili/ili-map-pwn30.tab

Requirements:

- The Wn Python library: https://github.com/goodmami/wn
- The Pe Python library: https://github.com/goodmami/pe
- WNDB source files: https://wordnet.princeton.edu/download/current-version

Partially inspired by the gwn-scala-api converter and the NLTK's WNDB
reader:

- https://github.com/jmccrae/gwn-scala-api
- https://github.com/nltk/nltk/blob/develop/nltk/corpus/reader/wordnet.py

Author: Michael Wayne Goodman (https://github.com/goodmami)
License: MIT

"""

import argparse
import csv
import logging
from pathlib import Path

# import wn
from wn._types import AnyPath
from wn.constants import LEXICOGRAPHER_FILES
from wn.util import ProgressHandler, ProgressBar, synset_id_formatter
from wn.lmf import (
    dump,
    Lexicon,
    Metadata,
    LexicalEntry,
    Lemma,
    Form,
    Sense,
    Count,
    Relation,
    Example,
    Synset,
    Definition,
    SyntacticBehaviour,
)

from . import wndb
from .glossparser import gloss_parser
from .util import escape_lemma, respace_word

log = logging.getLogger('wndb2lmf')

LMF_VERSION = "1.3"
REQUIRED_FILES = [
    "data.noun",
    "data.verb",
    "data.adj",
    "data.adv",
    "noun.exc",
    "verb.exc",
    "adj.exc",
    "adv.exc",
    "index.sense",
    "cntlist",
]


_Data = dict[str, dict[int, wndb.DataRecord]]
_SenseIndex = dict[str, dict[int, wndb.SenseInfo]]
_Exceptions = dict[str, dict[str, set[str]]]

# see: https://wordnet.princeton.edu/documentation/lexnames5wn
_lexfile_lookup = {num: lexfile for lexfile, num in LEXICOGRAPHER_FILES.items()}


# Main Function ########################################################


def main(args):
    source = Path(args.SRC).expanduser()
    progress = ProgressBar(
        message=f"Building {args.id}:{args.version}",
        refresh_interval=1000,
    )

    progress.flash("Inspecting sources")
    _inspect(source)

    progress.flash("Loading WNDB data")
    data = _load_data(source)

    progress.flash("Loading sense index")
    senseidx = _load_sense_index(source)

    progress.flash("Loading verb frames")
    syntactic_behaviours = _load_frames()

    progress.flash("Loading exception lists")
    exceptions = _load_exceptions(source)

    progress.flash("Loading ILI map")
    ilimap = {}
    if args.ili_map:
        ilimap = _load_ili_map(args.ili_map, args.ili_confidence_threshold)

    lexicon = Lexicon(
        id=args.id,
        version=args.version,
        label=args.label,
        language=args.language,
        email=args.email,
        license=args.license,
        url=args.url or "",
        citation=args.citation or "",
        logo=args.logo or "",
        requires=[],
        entries=[],
        synsets=[],
        frames=syntactic_behaviours,
    )

    progress.set(total=sum(map(len, data.values())))
    _build_lexicon(lexicon, data, senseidx, exceptions, ilimap, progress)

    progress.flash(f"Writing to WN-LMF {LMF_VERSION}")
    dump(
        {"lmf_version": LMF_VERSION, "lexicons": [lexicon]},
        args.DEST,
    )

    progress.flash(f"Built {args.id}:{args.version}")
    progress.close()


def _inspect(source: Path) -> None:
    for filename in REQUIRED_FILES:
        if not (source / filename).is_file():
            raise wndb.WNDBError(f"file not found or is not a regular file: {filename}")


# LMF Building Functions ###############################################


def _build_lexicon(
    lex: Lexicon,
    data: _Data,
    senseidx: _SenseIndex,
    exceptions: _Exceptions,
    ilimap: dict[str, str],
    progress: ProgressHandler,
) -> None:
    lex_id = lex["id"]
    _make_synset_id = synset_id_formatter(fmt=f"{lex_id}-{{offset:08}}-{{pos}}")

    for pos in "nvar":
        progress.set(status=pos)

        subdata = data[pos]

        entries: dict[str, LexicalEntry] = {}  # for random access to entries
        sense_rank: dict[str, int] = {}  # for sorting senses afterwards

        for offset, d in subdata.items():
            # First create the synset
            ssid = _make_synset_id(offset=offset, pos=d.ss_type)
            synset = _build_synset(d, ssid, ilimap, senseidx)
            lex["synsets"].append(synset)

            # Then create each entry (if not done yet) and sense for the synset
            word_w_num_map: dict[str, int] = {}
            w_num_sense_map: dict[int, Sense] = {}
            for w_num, w in enumerate(d.words, 1):
                if original_w_num := word_w_num_map.get(w):
                    log.warning(
                        "Suppressing redundant word %d (%s) for synset %s",
                        w_num,
                        w,
                        ssid
                    )
                    w_num_sense_map[w_num] = w_num_sense_map[original_w_num]
                    continue
                word_w_num_map[w] = w_num
                entry_id = _make_entry_id(lex_id, w.respaced, pos)
                if entry_id not in entries:
                    entry = _build_entry(d, entry_id, w, pos, exceptions)
                    entries[entry_id] = entry
                    lex["entries"].append(entry)

                sense_key, _, sense_num, count = senseidx[w.lemma][offset]
                sense_id = _make_sense_id(lex_id, w.respaced, offset, d.ss_type)
                sense = _build_sense(d, sense_id, ssid, count, w.adjposition, sense_key)

                synset["members"].append(sense_id)
                entries[entry_id]["senses"].append(sense)
                w_num_sense_map[w_num] = sense
                sense_rank[sense_id] = sense_num

            used_senserels: set[tuple[str, str, str]] = set()
            for p in d.pointers:
                relname = wndb.POINTER_MAP[p.pointer_symbol]
                tgt_offset = p.synset_offset
                tgt = data[p.pos][tgt_offset]
                if p.source_w_num or p.target_w_num:
                    src_sense = w_num_sense_map[p.source_w_num]
                    word = tgt.words[p.target_w_num - 1]  # 1-based indexing
                    target_id = _make_sense_id(
                        lex_id, word.respaced, tgt_offset, tgt.ss_type
                    )
                    used_key = (relname, src_sense["id"], target_id)
                    if used_key in used_senserels:
                        log.warning(
                            "Suppressing redundant sense relation: %s from %s to %s",
                            *used_key,
                        )
                    else:
                        src_sense["relations"].append(
                            Relation(target=target_id, relType=relname)
                        )
                        used_senserels.add(used_key)
                else:
                    target_id = _make_synset_id(offset=tgt_offset, pos=tgt.ss_type)
                    synset["relations"].append(
                        Relation(target=target_id, relType=relname)
                    )

            for f in d.frames:
                f_id = _make_frame_id(f.f_num)
                if f.w_num == 0:
                    for sense in w_num_sense_map.values():
                        sense.setdefault("subcat", []).append(f_id)
                elif f.w_num in w_num_sense_map:
                    w_num_sense_map[f.w_num].setdefault("subcat", []).append(f_id)
                else:
                    raise wndb.WNDBError("Frame {f.f_num} matches no sense: {f.w_num}")

            progress.update()

        # sort senses when done with a data file
        progress.set(status="sorting senses")
        for entry in entries.values():
            entry["senses"].sort(key=lambda s: sense_rank[s["id"]])

    # sort lexical entries when done with all
    lex["entries"].sort(key=lambda e: e["id"])


def _build_synset(
    d: wndb.DataRecord,
    ssid: str,
    ilimap: dict[str, str],
    senseidx: _SenseIndex,
) -> Synset:
    ili = ilimap.get(f"{d.synset_offset:08}-{d.ss_type}", "")
    definitions, examples = _parse_data_gloss(d.gloss)
    lemma = d.words[0].lemma
    return Synset(
        id=ssid,
        ili=ili,
        partOfSpeech=d.ss_type,
        definitions=[Definition(text=dfn) for dfn in definitions],
        relations=[],  # done later
        examples=[Example(text=ex) for ex in examples],
        lexicalized=True,
        members=[],
        lexfile=_lexfile_lookup.get(d.lex_filenum),
        meta=Metadata(
            identifier=_make_nltk_synset_name(
                lemma,
                d.ss_type,
                senseidx[lemma][d.synset_offset].sense_number,
            )
        ),
    )


def _build_entry(
    d: wndb.DataRecord,
    entry_id: str,
    w: wndb.Word,
    pos: str,
    exceptions: _Exceptions,
) -> LexicalEntry:
    exceptional_forms = sorted(exceptions[pos].get(w.word, set()))
    return LexicalEntry(
        id=entry_id,
        lemma=Lemma(writtenForm=w.respaced, partOfSpeech=pos),
        forms=[Form(writtenForm=respace_word(form)) for form in exceptional_forms],
        senses=[],
        meta=None,
    )


def _build_sense(
    d: wndb.DataRecord,
    sense_id: str,
    ssid: str,
    count: int,
    adjposition: str,
    sense_key: str,
) -> Sense:
    return Sense(
        id=sense_id,
        synset=ssid,
        relations=[],  # done later
        examples=[],
        counts=[Count(value=count)] if count else [],
        lexicalized=True,
        adjposition=adjposition if adjposition else "",
        meta=Metadata(identifier=sense_key),
    )


# File loading #########################################################


def _load_data(source: Path) -> _Data:
    return {
        "n": _load_data_file(source / "data.noun"),
        "v": _load_data_file(source / "data.verb"),
        "a": _load_data_file(source / "data.adj"),
        "r": _load_data_file(source / "data.adv"),
    }


def _load_data_file(path: Path) -> dict[int, wndb.DataRecord]:
    return {record.synset_offset: record for record in wndb.read_data_file(path)}


def _load_sense_index(path: Path) -> _SenseIndex:
    cntmap = {c.sense_key: c.tag_cnt for c in wndb.read_count_list(path / "cntlist")}
    senseidx: _SenseIndex = {}
    for senseinfo in wndb.read_sense_index(path / "index.sense"):
        sense_key = senseinfo.sense_key
        lemma = wndb.sense_key_lemma(sense_key)
        if lemma not in senseidx:
            senseidx[lemma] = {}
        if senseinfo.tag_cnt not in (-1, cntmap.get(sense_key, 0)):
            log.info("Tag count in sense index differs for %s", sense_key)
        # use cntlist count instead of index.sense count
        senseinfo = senseinfo._replace(tag_cnt=cntmap.get(sense_key, 0))
        senseidx[lemma][senseinfo.synset_offset] = senseinfo
    return senseidx


def _load_frames() -> list[SyntacticBehaviour]:
    frames = [
        SyntacticBehaviour(id=_make_frame_id(f_num), subcategorizationFrame=subcat)
        for f_num, subcat in wndb.VERB_FRAMES
    ]
    return frames


def _load_exceptions(source: Path) -> _Exceptions:
    return {
        "n": _load_exceptions_file(source / "noun.exc"),
        "v": _load_exceptions_file(source / "verb.exc"),
        "a": _load_exceptions_file(source / "adj.exc"),
        "r": _load_exceptions_file(source / "adv.exc"),
    }


def _load_exceptions_file(path: Path) -> dict[str, set[str]]:
    exceptions: dict[str, set[str]] = {}
    for exc in wndb.read_exceptions_file(path):
        for base_form in exc.base_forms:
            if base_form not in exceptions:
                exceptions[base_form] = set()
            exceptions[base_form].add(exc.form)
    return exceptions


def _load_ili_map(path: AnyPath, threshold: float) -> dict[str, str]:
    path = Path(path).expanduser()
    ili_map = {}
    with path.open(newline="") as csvfile:
        reader = csv.reader(csvfile, dialect="excel-tab")
        for ili, ssid, *extra in reader:
            if extra and float(extra[0]) < threshold:
                log.info(
                    "ILI map confidence doesn't meet the threshold: %s < %g",
                    extra[0],
                    threshold
                )
                continue
            ili_map[ssid] = ili
    return ili_map


# Helper functions #####################################################

def _parse_data_gloss(gloss: str) -> tuple[list[str], list[str]]:
    clean_gloss = gloss.strip().strip("; ")
    if not clean_gloss.strip():
        return [], []
    match = gloss_parser.match(clean_gloss)
    if not match:
        return [clean_gloss], []
    else:
        definition, raw_examples = match.groups()
        examples: list[str] = []
        for ex in raw_examples:
            ex = ex.strip()
            if ex == '"':
                continue
            elif ex.count('"') == 2 and ex.startswith('"') and ex.endswith('"'):
                ex = ex[1:-1]
            examples.append(ex)
        return [definition.strip()], examples


def _make_frame_id(f_num: int) -> str:
    return f"frame-{f_num}"


def _make_entry_id(id: str, word: str, pos: str) -> str:
    return f"{id}-{escape_lemma(word)}-{pos}"


def _make_sense_id(
    id: str,
    word: str,
    offset: int,
    pos: str,
) -> str:
    return f"{id}-{escape_lemma(word)}-{offset:08}-{pos}"


def _make_nltk_synset_name(lemma: str, ss_type: str, sense_num: int) -> str:
    return f"{lemma}.{ss_type}.{sense_num:02}"


# Command usage

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Convert WNDB to WN-LMF")
    parser.add_argument("SRC", help="path to the WNDB directory")
    parser.add_argument("DEST", help="path the the destination file")
    parser.add_argument("--id", required=True, help="the lexicon identifier")
    parser.add_argument(
        "--label", default="Unknown wordnet", help="a descriptive label for the lexicon"
    )
    parser.add_argument("--language", default="und", help="the language of the lexicon")
    parser.add_argument(
        "--email",
        default="maintainer@example.com",
        help="the maintainer's email address",
    )
    parser.add_argument(
        "--license", default="No license", help="the license of the lexicon"
    )
    parser.add_argument("--version", default="0", help="the version of this lexicon")
    parser.add_argument("--url", help="a URL for the project")
    parser.add_argument("--citation", help="a citation for the project")
    parser.add_argument("--logo", help="a URL for a logo for the project")
    parser.add_argument("--ili-map", help="a file mapping ILI IDs to synset IDs")
    parser.add_argument(
        "--ili-confidence-threshold",
        type=float,
        metavar="THRESHOLD",
        help="ignore ILI mappings below the confidence threshold (default: 0.0)",
        default=0.0,
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    main(args)
