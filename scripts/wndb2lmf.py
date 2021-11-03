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

from typing import Optional, Tuple, Dict, Set, List, NamedTuple
from pathlib import Path
import csv
import argparse

import pe

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
    SenseRelation,
    Example,
    Synset,
    SynsetRelation,
    Definition,
    SyntacticBehaviour,
)

from .util import escape_lemma


LMF_VERSION = '1.1'


# Data and Data Types ##################################################

class WNDBError(Exception):
    """Raised on invalid WNDB databases."""


class Word(NamedTuple):
    word: str
    # lex_id: int
    adjposition: Optional[str]


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
    words: List[Word]
    pointers: List[Pointer]
    frames: List[Frame]
    gloss: str


# see: https://wordnet.princeton.edu/documentation/wninput5wn
_pointer_map = {
    '!': 'antonym',
    '@': 'hypernym',
    '@i': 'instance_hypernym',
    '~': 'hyponym',
    '~i': 'instance_hyponym',
    '#m': 'holo_member',
    '#s': 'holo_substance',
    '#p': 'holo_part',
    '%m': 'mero_member',
    '%s': 'mero_substance',
    '%p': 'mero_part',
    '=': 'attribute',
    '+': 'derivation',
    ';c': 'domain_topic',
    '-c': 'has_domain_topic',
    ';r': 'domain_region',
    '-r': 'has_domain_region',
    ';u': 'is_exemplified_by',  # was: domain usage
    '-u': 'exemplifies',  # was: in domain usage
    '*': 'entails',
    '>': 'causes',
    '^': 'also',
    '$': 'similar',  # was: verb group
    '&': 'similar',
    '<': 'participle',
    '\\': 'pertainym',
}

_Data = Dict[str, Dict[int, DataRecord]]
_SenseIndex = Dict[str, Dict[int, Tuple[str, int, int]]]
_Exceptions = Dict[str, Dict[str, Set[str]]]

# see: https://wordnet.princeton.edu/documentation/lexnames5wn
_lexfile_lookup = {num: lexfile for lexfile, num in LEXICOGRAPHER_FILES.items()}


# Main Function ########################################################

def main(args):
    source = Path(args.SRC).expanduser()
    progress = ProgressBar(message=f'Building {args.id}:{args.version}',
                           refresh_interval=1000)

    progress.flash('Inspecting sources')
    _inspect(source)

    progress.flash('Loading WNDB data')
    data = _load_data(source)

    progress.flash('Loading sense index')
    senseidx = _load_sense_index(source / 'index.sense')

    progress.flash('Loading verb frames')
    syntactic_behaviours = _load_frames(source / 'verb.Framestext')

    progress.flash('Loading exception lists')
    exceptions = _load_exceptions(source)

    progress.flash('Loading ILI map')
    ilimap = _load_ili_map(args.ili_map) if args.ili_map else {}

    lexicon = Lexicon(
        args.id,
        args.label,
        args.language,
        args.email,
        args.license,
        args.version,
        url=args.url or '',
        citation=args.citation or '',
        logo=args.logo or '',
        syntactic_behaviours=syntactic_behaviours
    )

    progress.set(total=sum(map(len, data.values())))
    _build_lexicon(lexicon, data, senseidx, exceptions, ilimap, progress)

    progress.flash(f'Writing to WN-LMF {LMF_VERSION}')
    dump([lexicon], args.DEST, version=LMF_VERSION)

    progress.flash(f'Built {args.id}:{args.version}')
    progress.close()


def _inspect(source: Path) -> None:
    for filename in ('data.noun', 'data.verb', 'data.adj', 'data.adv',
                     'noun.exc', 'verb.exc', 'adj.exc', 'adv.exc',
                     'index.sense', 'verb.Framestext'):
        if not (source / filename).is_file():
            raise WNDBError(f'file not found or is not a regular file: {filename}')


# LMF Building Functions ###############################################

def _build_lexicon(
    lex: Lexicon,
    data: _Data,
    senseidx: _SenseIndex,
    exceptions: _Exceptions,
    ilimap: Dict[str, str],
    progress: ProgressHandler,
) -> None:
    _make_synset_id = synset_id_formatter(fmt=f'{lex.id}-{{offset:08}}-{{pos}}')
    frame_sense_map = {sb.id: sb.senses for sb in lex.syntactic_behaviours}

    for pos in 'nvar':
        progress.set(status=pos)

        entries: Dict[str, LexicalEntry] = {}  # for random access to entries
        sense_rank: Dict[str, int] = {}  # for sorting senses afterwards

        for offset, d in data[pos].items():

            # First create the synset
            ssid = _make_synset_id(offset=offset, pos=d.ss_type)
            synset = _build_synset(d, ssid, ilimap, senseidx)
            lex.synsets.append(synset)

            # Then create each entry (if not done yet) and sense for the synset
            w_num_sense_map: Dict[int, Sense] = {}
            for w_num, w in enumerate(d.words, 1):
                lemma = w.word

                entry_id = _make_entry_id(lex.id, lemma, pos)
                if entry_id not in entries:
                    entry = _build_entry(d, entry_id, lemma, pos, exceptions)
                    entries[entry_id] = entry
                    lex.lexical_entries.append(entry)

                sense_key, sense_num, count = senseidx[lemma.lower()][offset]
                sense_id = _make_sense_id(lex.id, lemma, offset, d.ss_type)
                sense = _build_sense(d, sense_id, ssid, count, w.adjposition, sense_key)

                synset.members.append(sense.id)
                entries[entry_id].senses.append(sense)
                w_num_sense_map[w_num] = sense
                sense_rank[sense.id] = sense_num

            for p in d.pointers:
                relname = _pointer_map[p.pointer_symbol]
                tgt_offset = p.synset_offset
                tgt = data[p.pos][tgt_offset]
                if p.source_w_num or p.target_w_num:
                    src_sense = w_num_sense_map[p.source_w_num]
                    lemma = tgt.words[p.target_w_num - 1].word  # 1-based indexing
                    target_id = _make_sense_id(lex.id, lemma, tgt_offset, tgt.ss_type)
                    src_sense.relations.append(SenseRelation(target_id, relname))
                else:
                    target_id = _make_synset_id(offset=tgt_offset, pos=tgt.ss_type)
                    synset.relations.append(SynsetRelation(target_id, relname))

            for f in d.frames:
                f_id = _make_frame_id(f.f_num)
                if f.w_num == 0:
                    sense_ids = [s.id for s in w_num_sense_map.values()]
                    frame_sense_map[f_id].extend(sense_ids)
                elif f.w_num in w_num_sense_map:
                    frame_sense_map[f_id].append(w_num_sense_map[f.w_num].id)

            progress.update()

        # sort senses when done with a data file
        progress.set(status='sorting senses')
        for entry in entries.values():
            entry.senses.sort(key=lambda s: sense_rank[s.id])

    # sort lexical entries when done with all
    lex.lexical_entries.sort(key=lambda e: e.id)


def _build_synset(
    d: DataRecord,
    ssid: str,
    ilimap: Dict[str, str],
    senseidx: _SenseIndex
) -> Synset:
    ili = ilimap.get(f'{d.synset_offset:08}-{d.ss_type}')
    definition, examples = _parse_data_gloss(d.gloss)
    first_word = d.words[0].word
    return Synset(
        ssid,
        ili=ili,
        pos=d.ss_type,
        definitions=[Definition(definition)],
        examples=[Example(ex) for ex in examples],
        lexicalized=True,
        members=[],
        lexfile=_lexfile_lookup.get(d.lex_filenum),
        meta=Metadata(
            identifier=_make_nltk_synset_name(
                first_word,
                d.ss_type,
                senseidx[first_word.lower()][d.synset_offset][1]
            )
        )
    )


def _build_entry(
    d: DataRecord,
    entry_id: str,
    lemma: str,
    pos: str,
    exceptions: _Exceptions,
) -> LexicalEntry:
    exceptional_forms = sorted(exceptions[pos].get(lemma.lower(), set()))
    return LexicalEntry(
        entry_id,
        Lemma(_normalize_form(lemma), pos),
        forms=[Form(None, _normalize_form(form), None)
               for form in exceptional_forms],
        senses=[],
        meta=None
    )


def _build_sense(
    d: DataRecord,
    sense_id: str,
    ssid: str,
    count: int,
    adjposition: Optional[str],
    sense_key: str,
) -> Sense:
    return Sense(
        sense_id,
        ssid,
        relations=None,  # done later
        examples=None,
        counts=[Count(count)] if count else None,
        lexicalized=True,
        adjposition=adjposition,
        meta=Metadata(identifier=sense_key)
    )


# File loading #########################################################


def _load_data(source: Path) -> _Data:
    return {
        'n': _load_data_file(source / 'data.noun'),
        'v': _load_data_file(source / 'data.verb'),
        'a': _load_data_file(source / 'data.adj'),
        'r': _load_data_file(source / 'data.adv'),
    }


def _load_data_file(path: Path) -> Dict[int, DataRecord]:
    subdata: Dict[int, DataRecord] = {}
    with path.open('rt') as datafile:
        for line in datafile:
            if line.startswith('  '):
                continue  # skip header
            record = _parse_data_line(line)
            subdata[record.synset_offset] = record
    return subdata


def _load_sense_index(path: Path) -> _SenseIndex:
    senseidx: _SenseIndex = {}
    with path.open('rt') as indexfile:
        for line in indexfile:
            sense_key, offset, sense_number, tag_cnt = line.split()
            lemma = sense_key[:sense_key.index('%')].lower()
            if lemma not in senseidx:
                senseidx[lemma] = {}
            senseidx[lemma][int(offset)] = (sense_key, int(sense_number), int(tag_cnt))
    return senseidx


def _load_frames(path: Path) -> List[SyntacticBehaviour]:
    frames = []
    with path.open('rt') as framefile:
        for line in framefile:
            f_num, subcat = line.strip().split(maxsplit=1)
            frames.append(SyntacticBehaviour(
                id=_make_frame_id(int(f_num)),
                frame=subcat.strip()
            ))
    return frames


def _load_exceptions(source: Path) -> _Exceptions:
    return {
        'n': _load_exceptions_file(source / 'noun.exc'),
        'v': _load_exceptions_file(source / 'verb.exc'),
        'a': _load_exceptions_file(source / 'adj.exc'),
        'r': _load_exceptions_file(source / 'adv.exc'),
    }


def _load_exceptions_file(path: Path) -> Dict[str, Set[str]]:
    exceptions: Dict[str, Set[str]] = {}
    with path.open('rt') as exceptionfile:
        for line in exceptionfile:
            form, *roots = line.split()
            for root in roots:
                if root not in exceptions:
                    exceptions[root] = set()
                exceptions[root].add(form)
    return exceptions


def _load_ili_map(path: AnyPath) -> Dict[str, str]:
    path = Path(path).expanduser()
    ili_map = {}
    with path.open(newline='') as csvfile:
        reader = csv.reader(csvfile, dialect='excel-tab')
        for ili, ssid in reader:
            ili_map[ssid] = ili
    return ili_map


# Field parsing ########################################################

def _parse_data_line(line: str) -> DataRecord:
    nongloss, _, gloss = line.partition('|')
    synset_offset, lex_filenum, ss_type, _w_cnt, *rest = nongloss.split(' ')

    w_cnt = int(_w_cnt, 16)          # word count is hexadecimal
    w_idx = w_cnt * 2                # each w is 2 columns: word, lex_id
    p_cnt = int(rest[w_idx])         # pointer count is decimal
    p_idx = w_idx + 1 + (p_cnt * 4)  # 4 cols: sym, offset, pos, src_tgt
    if len(rest) > p_idx and rest[p_idx]:
        f_cnt = int(rest[p_idx])     # frame count is decimal
    else:
        f_cnt = 0

    return DataRecord(
        int(synset_offset),
        int(lex_filenum),
        ss_type,
        _parse_data_words(ss_type, rest[:w_idx], w_cnt),
        _parse_data_pointers(rest[w_idx+1:p_idx], p_cnt),
        _parse_data_frames(rest[p_idx+1:], f_cnt),
        gloss
    )


def _parse_data_words(
    ss_type: str,
    xs: List[str],
    w_cnt: int,
) -> List[Word]:
    words = []
    for lemma, _ in zip(xs[::2], xs[1::2]):  # _ is lex_id, ignored for now
        lemma, adjposition = _split_adjposition(lemma, ss_type)
        words.append(Word(lemma, adjposition))
    assert len(words) == w_cnt, f'{len(words)=} {w_cnt=}'
    return words


def _parse_data_pointers(
    xs: List[str],
    p_cnt: int
) -> List[Pointer]:
    pointers = []
    for sym, offset, pos, src_tgt in zip(xs[::4], xs[1::4], xs[2::4], xs[3::4]):
        src, tgt = src_tgt[:2], src_tgt[2:]
        pointers.append(Pointer(sym, int(offset), pos, int(src, 16), int(tgt, 16)))
    assert len(pointers) == p_cnt, f'{len(pointers)=} {p_cnt=}'
    return pointers


def _parse_data_frames(
    xs: List[str],
    f_cnt: int
) -> List[Frame]:
    frames = []
    for _, f_num, w_num in zip(xs[::3], xs[1::3], xs[2::3]):
        frames.append(Frame(int(f_num), int(w_num, 16)))
    assert len(frames) == f_cnt
    return frames


# This grammar may be fragile against non PWN-3.0 versions of wordnet!
_gloss_pe = pe.compile(
    '''
    Start      <- ~Definition (DELIM Example)* EOS
    Definition <- ( !DELIM (![(] . / Paren) )+
    Paren      <- '(' (![)] .)* ')'    # assume parentheticals are closed
    Example    <- ~(Quote (NonQuote Quote?)*) SPACE*
    Quote      <- ["] InQuote* ["]     # regular string
                / ["] InQuote* EOS     # missing end-quote
                / !DELIM InQuote* ["]  # missing start-quote
    InQuote    <- !["] .               # non-quote chars
                / ["] [A-Za-z]         # correcting for typos (e.g., 'I"m')
    NonQuote   <- (!DELIM . (',' SPACE* &["])?)+
    DELIM      <- [;:,] SPACE* &["]
    SPACE      <- ' '
    EOS        <- !.
    ''',
    flags=(pe.MEMOIZE | pe.STRICT | pe.OPTIMIZE)
)


def _parse_data_gloss(gloss: str) -> Tuple[str, List[str]]:
    clean_gloss = gloss.strip().strip('; ')
    match = _gloss_pe.match(clean_gloss)
    if not match:
        return clean_gloss, []
    else:
        definition, *raw_examples = match.groups()
        examples: List[str] = []
        for ex in raw_examples:
            ex = ex.strip()
            if ex.count('"') == 2 and ex.startswith('"') and ex.endswith('"'):
                ex = ex[1:-1]
            examples.append(ex)
        return definition.strip(), examples


# Helper functions #####################################################

# For now we're getting these from index.sense, but this is the code
# for creating them from the data.
#
# def _make_sense_key(
#     lemma: str,
#     lex_filenum: int,
#     lex_id: int,
#     head_word: str = '',
#     head_id: int = 0,
# ) -> str:
#     h_id = f'{head_id:02}' if head_word else ''
#     return f'{lemma}%{lex_filenum:02}:{lex_id:02}:{head_word}:{h_id}'


def _make_frame_id(f_num: int) -> str:
    return f'frame-{f_num}'


def _make_entry_id(id: str, lemma: str, pos: str) -> str:
    return f'{id}-{escape_lemma(lemma)}-{pos}'


def _make_sense_id(
    id: str,
    lemma: str,
    offset: int,
    pos: str,
) -> str:
    return f'{id}-{escape_lemma(lemma)}-{offset:08}-{pos}'


def _make_nltk_synset_name(lemma: str, ss_type: str, sense_num: int) -> str:
    return f'{lemma.lower()}.{ss_type}.{sense_num:02}'


def _split_adjposition(lemma: str, ss_type: str) -> Tuple[str, Optional[str]]:
    if ss_type in 'as' and lemma.endswith(')'):
        if lemma.endswith('(a)'):
            return lemma[:-3], 'a'
        elif lemma.endswith('(p)'):
            return lemma[:-3], 'p'
        elif lemma.endswith('(ip)'):
            return lemma[:-4], 'ip'
    return lemma, None


def _normalize_form(form: str) -> str:
    return form.replace('_', ' ')


# Command usage

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Convert WNDB to WN-LMF')
    parser.add_argument('SRC',
                        help='path to the WNDB directory')
    parser.add_argument('DEST',
                        help='path the the destination file')
    parser.add_argument('--id', required=True,
                        help='the lexicon identifier')
    parser.add_argument('--label', default='Unknown wordnet',
                        help='a descriptive label for the lexicon')
    parser.add_argument('--language', default='und',
                        help='the language of the lexicon')
    parser.add_argument('--email', default='maintainer@example.com',
                        help='the maintainer\'s email address')
    parser.add_argument('--license', default='No license',
                        help='the license of the lexicon')
    parser.add_argument('--version', default='0',
                        help='the version of this lexicon')
    parser.add_argument('--url',
                        help='a URL for the project')
    parser.add_argument('--citation',
                        help='a citation for the project')
    parser.add_argument('--logo',
                        help='a URL for a logo for the project')
    parser.add_argument('--ili-map',
                        help='a file mapping ILI IDs to synset IDs')
    args = parser.parse_args()
    main(args)
