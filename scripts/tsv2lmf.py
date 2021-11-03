#
# Take an OMW 1.0 wordnet TSV and convert to WN-LMF 1.1
#

from typing import Optional, Tuple, TextIO
import sys
from pathlib import Path
from collections import Counter

from wn.lmf import (
    dump,
    Lexicon,
    # Metadata,
    LexicalEntry,
    Lemma,
    Form,
    Sense,
    Example,
    Synset,
    Definition,
)

from .util import escape_lemma

LMF_VERSION = '1.1'

# PATHS ################################################################

OMWDATA = Path(__file__).parent.parent
ILIFILE = OMWDATA / 'etc' / 'cili' / 'ili-map-pwn30.tab'
LOGDIR = OMWDATA / 'log'
LOGDIR.mkdir(exist_ok=True)

# CONSTANTS ############################################################

bcp47 = {
    "als": "sq",        # Albanian
    "arb": "arb",       # Arabic
    "bul": "bg",        # Bulgarian
    "cmn": "cmn-Hans",  # Mandarin Chinese (Simplified)
    "qcn": "cmn-Hant",  # Mandarin Chinese (Traditional)
    "dan": "da",        # Danish
    "ell": "el",        # Greek
    "eng": "en",        # English
    "fas": "fa",        # Farsi
    "fin": "fi",        # Finnish
    "fra": "fr",        # French
    "heb": "he",        # Hebrew
    "hrv": "hr",        # Croation
    "isl": "is",        # Icelandic
    "ita": "it",        # Italian
    "jpn": "ja",        # Japanese
    "cat": "ca",        # Catalan
    "eus": "eu",        # Basque
    "glg": "gl",        # Galician
    "spa": "es",        # Spanish
    "ind": "id",        # Indonesian
    "zsm": "zsm",       # Standard Malay
    "nld": "nl",        # Dutch
    "nno": "nn",        # Norwegian (Norsk)
    "nob": "nb",        # Norwegian (Bokmal)
    "pol": "pl",        # Polish
    "por": "pt",        # Portuguese
    "ron": "ro",        # Romanian
    "lit": "lt",        # Lithuanian
    "slk": "sk",        # Slovak
    "slv": "sl",        # Slovene
    "swe": "sv",        # Swedish
    "tha": "th",        # Thai
}

open_license = {
    'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0/',
    'CC-BY 3.0': 'https://creativecommons.org/licenses/by/3.0/',
    'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/',
    'CC BY SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/',
    'CC BY-SA': 'https://creativecommons.org/licenses/by-sa/',
    'CC BY SA': 'https://creativecommons.org/licenses/by-sa/',
    'CC BY SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
    'Apache 2.0': 'https://opensource.org/licenses/Apache-2.0',
    'CeCILL-C': 'http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html',
    'MIT': 'https://opensource.org/licenses/MIT/',
    'wordnet': 'wordnet',
    'unicode': 'https://www.unicode.org/license.html',
    'ODC-BY 1.0': 'http://opendefinition.org/licenses/odc-by/'
}


# MAIN FUNCTION ########################################################

def convert(
    source: str,
    outfile: str,
    lexid: str,
    label: str,
    language: str,
    email: str,
    license: str,
    version: str,
    url: Optional[str] = None,
    citation: Optional[str] = None,
    logo: Optional[str] = None,
    requires: Optional[dict] = None,
    meta: Optional[dict] = None,
):
    logpath = LOGDIR / f'tsv2lmf_{lexid}-{version}.log'
    with logpath.open('w') as logfile:
        lex = Lexicon(
            lexid,
            label,
            bcp47.get(language, language),
            email,
            license,
            version,
            url=url,
            citation=citation,
            logo=logo,
            meta=meta,
            # meta=Metadata(
            #     publisher=PUBLISHER,
            #     description=DESCRIPTION,
            #     confidence=CONFIDENCE_SCORE,
            # )
        )
        if requires:
            lex.requires.append(requires)

        entries, senses, synsets = load(source, lex, logfile)
        build(lex, entries, senses, synsets, logfile)

    dump([lex], outfile, version=LMF_VERSION)


# DATA LOADING AND VALIDATION ##########################################

def load(source: str, lex: Lexicon, logfile: TextIO):
    entries = {}
    senses = {}
    synsets = {}

    ilimap = _load_ili()

    with open(source, 'rt') as tabfile:
        label, lang, url, license = _check_header(tabfile, lex, logfile)
        prefix = f'{lang}:'
        for line in tabfile:
            if not line.strip() or line.startswith('#'):
                continue
            offset_pos, type_, *content = line.split('\t')
            offset_pos = offset_pos.strip()

            ili = ilimap.get(offset_pos)

            ssid = synset_id(lex.id, offset_pos)
            pos = ssid[-1]
            if ssid not in synsets:
                synsets[ssid] = {'pos': pos, 'ili': ili,
                                 'members': [], 'def': [], 'exe': []}
            ss = synsets[ssid]

            type_ = type_.removeprefix(prefix)  # only match for current language
            if type_ == 'lemma':
                lemma = _clean_lemma(content[0], logfile)
                eid = entry_id(lex.id, lemma, pos)
                if eid not in entries:
                    entries[eid] = {'lemma': lemma, 'pos': pos, 'senses': []}
                sid = sense_id(lex.id, lemma, offset_pos[:-2], pos)
                entries[eid]['senses'].append(sid)
                senses[sid] = ssid
                ss['members'].append(sid)

            elif type_ in ('def', 'exe'):
                order, text = content
                ss[type_].append((int(order), text.strip()))

            else:
                print(f'IGNORING: {line.strip()}', file=logfile)

    return entries, senses, synsets


def _load_ili():
    ilimap = {}
    with ILIFILE.open('rt') as ilifile:
        for line in ilifile:
            ili, ssid = line.strip().split('\t')
            ilimap[ssid] = ili
            if ssid.endswith('-s'):
                ilimap[ssid[:-2] + '-a'] = ili  # map as either -s or -a
    return ilimap


def _check_header(
    tabfile: TextIO,
    lex: Lexicon,
    logfile: TextIO
) -> Tuple[str, str, str, str]:
    if not tabfile.buffer.peek(1).startswith(b'#'):
        print('NO META DATA', file=sys.stderr)
        print('NO META DATA', file=logfile)
        label = lang = url = license = 'n/a'
    else:
        header = next(tabfile).lstrip('#').strip()
        label, lang, url, license = header.split('\t')
        if lang not in bcp47:
            print(f'UNKNOWN LANGUAGE: {lang}', file=sys.stderr)
            print(f'UNKNOWN LANGUAGE: {lang}', file=logfile)
        elif bcp47[lang] != lex.language:
            print('INDEX INCONSISTENT WITH SOURCE: '
                  f'{bcp47[lang]} != {lex.language}')
        if license not in open_license:
            print(f'UNKNOWN LICENSE: {license}', file=sys.stderr)
            print(f'UNKNOWN LICENSE: {license}', file=logfile)
        elif open_license[license] != lex.license:
            print('INDEX INCONSISTENT WITH SOURCE: '
                  f'{open_license[license]} != {lex.license}')
    return label, lang, url, license


def _clean_lemma(lemma: str, logfile: TextIO) -> str:
    lemma = lemma.strip()
    if lemma.startswith('"') and lemma.endswith('"'):
        lemma = lemma[1:-1]
        print('CLEANED: {} (removed start and end double quote)'.format(lemma),
              file=logfile)
    if '"' in lemma:
        print('WARNING: {} (contains a double quote)'.format(lemma),
              file=logfile)
    lemma = lemma.replace('_', ' ')
    return lemma


# LEXICON BUILDING AND VALIDATION ######################################

def build(
    lex: Lexicon,
    entries: dict,
    senses: dict,
    synsets: dict,
    logfile: TextIO
) -> None:
    for eid, entry in entries.items():
        sids = set(entry['senses'])
        # validate senses
        sense_counts = Counter(entry['senses'])
        for sid, count in (sense_counts - Counter(sids)).items():
            print(f'REDUNDANT SENSE: {sid} ({count + 1} occurrences)',
                  file=logfile)

        lex.lexical_entries.append(
            LexicalEntry(
                eid,
                Lemma(entry['lemma'], entry['pos']),
                senses=[Sense(sid, senses[sid]) for sid in sids]
            )
        )

    for ssid, synset in synsets.items():
        if len(synset['members']) == 0:
            print(f'EMPTY SYNSET: {ssid}', file=logfile)
            continue

        lex.synsets.append(
            Synset(
                ssid,
                ili=synset['ili'],
                pos=synset['pos'],
                definitions=[Definition(text)
                             for _, text in sorted(synset['def'])],
                examples=[Example(text)
                          for _, text in sorted(synset['exe'])],
                members=synset['members'],
            )
        )


# ID FORMATTERS ########################################################

def synset_id(lexid: str, ssid: str) -> str:
    if ssid.endswith('-s'):
        ssid = ssid[:-2] + '-a'
    return f'{lexid}-{ssid}'


def entry_id(lexid: str, lemma: str, pos: str) -> str:
    return f'{lexid}-{escape_lemma(lemma)}-{pos}'


def sense_id(lexid: str, lemma: str, ssid: str, pos: str) -> str:
    return f'{lexid}-{escape_lemma(lemma)}-{ssid}-{pos}'
