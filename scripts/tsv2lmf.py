#
# Take an OMW 1.0 wordnet TSV and convert to WN-LMF 1.3
#

import argparse
import logging
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wn.lmf import (
    dump,
    LexicalResource,
    Lexicon,
    Metadata,
    LexicalEntry,
    Lemma,
    Tag,
    Pronunciation,
    Form,
    Sense,
    Count,
    Example,
    Synset,
    Definition,
    Dependency,
)

if __name__ == "__main__":
    from util import escape_lemma, load_ili_map, PathLike
else:
    from .util import escape_lemma, load_ili_map, PathLike


LMF_VERSION = "1.3"

log = logging.getLogger("tsv2lmf")
log.setLevel(logging.INFO)  # not configurable at the moment


# CONSTANTS ############################################################

BCP47 = {
    "als": "sq",  # Albanian
    "arb": "arb",  # Arabic
    "bul": "bg",  # Bulgarian
    "cmn": "cmn-Hans",  # Mandarin Chinese (Simplified)
    "qcn": "cmn-Hant",  # Mandarin Chinese (Traditional)
    "dan": "da",  # Danish
    "ell": "el",  # Greek
    "eng": "en",  # English
    "fas": "fa",  # Farsi
    "fin": "fi",  # Finnish
    "fra": "fr",  # French
    "heb": "he",  # Hebrew
    "hrv": "hr",  # Croation
    "isl": "is",  # Icelandic
    "ita": "it",  # Italian
    "jpn": "ja",  # Japanese
    "cat": "ca",  # Catalan
    "eus": "eu",  # Basque
    "glg": "gl",  # Galician
    "spa": "es",  # Spanish
    "ind": "id",  # Indonesian
    "zsm": "zsm",  # Standard Malay
    "nld": "nl",  # Dutch
    "nno": "nn",  # Norwegian (Norsk)
    "nob": "nb",  # Norwegian (Bokmal)
    "pol": "pl",  # Polish
    "por": "pt",  # Portuguese
    "ron": "ro",  # Romanian
    "lit": "lt",  # Lithuanian
    "slk": "sk",  # Slovak
    "slv": "sl",  # Slovene
    "swe": "sv",  # Swedish
    "tha": "th",  # Thai
    "vie": "vi",  # Vietnamese
}

OPEN_LICENSES = {
    "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC-BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC BY SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "CC BY-SA": "https://creativecommons.org/licenses/by-sa/",
    "CC BY SA": "https://creativecommons.org/licenses/by-sa/",
    "CC BY SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "Apache 2.0": "https://opensource.org/licenses/Apache-2.0",
    "CeCILL-C": "http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html",
    "MIT": "https://opensource.org/licenses/MIT/",
    "wordnet": "wordnet",
    "unicode": "https://www.unicode.org/license.html",
    "ODC-BY 1.0": "http://opendefinition.org/licenses/odc-by/",
}


# INTERMEDIATE DATA STRUCTURES #########################################


@dataclass
class EntryData:
    id: str
    pos: str
    forms: list[Form] = field(default_factory=list)
    senses: dict[str, Sense] = field(default_factory=dict)


@dataclass
class SynsetData:
    id: str
    pos: str
    members: dict[str, Sense] = field(default_factory=dict)
    definitions: list[tuple[int, str]] = field(default_factory=list)
    examples: list[tuple[int, str]] = field(default_factory=list)
    lexicalized: bool = True


@dataclass
class TSVData:
    lex_id: str
    label: str = ""
    language: str = ""
    url: str = ""
    license: str = ""
    synsets: dict[str, SynsetData] = field(default_factory=dict)
    entries: dict[str, EntryData] = field(default_factory=dict)
    # for bookkeeping
    prev_pwn_id: str = ""
    prev_lemma: str = ""
    sense_counts: Counter = field(default_factory=Counter)


# EXCEPTIONS ###########################################################


class TSV2LMFError(Exception):
    """Raised on unexpected input in a TSV file."""


# MAIN FUNCTION ########################################################


def main(args: argparse.Namespace) -> int:
    source = Path(args.SOURCE)
    if not source.is_file():
        raise ValueError("source file not found")
    destination = Path(args.DESTINATION)

    if args.requires:
        id, _, ver = args.requires.partition(":")
        requires = Dependency(id=id, version=ver)
    else:
        requires = None

    if args.meta:
        meta = Metadata(**dict(kv.split("=", 1) for kv in args.meta))
    else:
        meta = None

    if args.ili_map:
        ilimap = load_ili_map(args.ili_map)
    else:
        ilimap = None

    convert(
        source,
        destination,
        args.id,
        args.label,
        args.language,
        args.email,
        args.license,
        args.version,
        url=args.url,
        citation=args.citation,
        logo=args.logo,
        requires=requires,
        meta=meta,
        ilimap=ilimap,
        logfile=args.log,
        abort_on_errors=args.abort_on_errors,
    )

    return 0


def convert(
    source: PathLike,
    outfile: PathLike,
    lexid: str,
    label: str,
    language: str,
    email: str,
    license: str,
    version: str,
    url: Optional[str] = None,
    citation: Optional[str] = None,
    logo: Optional[str] = None,
    requires: Optional[Dependency] = None,
    meta: Optional[Metadata] = None,
    ilimap: Optional[dict[str, str]] = None,
    logfile: PathLike = "",
    abort_on_errors: bool = False,
) -> None:
    if logfile:
        logging.basicConfig(filename=str(logfile), filemode="w", force=True)
    else:
        logging.basicConfig()

    log.info("Converting %s:%s [%s]: %s", lexid, version, language, source)

    lex = Lexicon(
        id=lexid,
        label=label,
        language=BCP47.get(language, language),
        email=email,
        license=license,
        version=version,
        url=url,
        citation=citation,
        logo=logo,
        requires=[],
        entries=[],
        synsets=[],
        meta=meta,
    )
    if requires:
        lex["requires"].append(requires)

    if ilimap is None:
        ilimap = {}

    data = load(Path(source), lex["id"], abort_on_errors=abort_on_errors)
    process_lexical_gaps(data)
    validate(lex, data)
    build(lex, data, ilimap)

    resource = LexicalResource(lmf_version=LMF_VERSION, lexicons=[lex])
    dump(resource, outfile)


# DATA LOADING AND VALIDATION ##########################################


def _load_header(data: TSVData, line: str) -> None:
    header = line.lstrip("#").strip()
    try:
        data.label, data.language, data.url, data.license = header.split("\t")
    except ValueError as exc:
        raise TSV2LMFError(f"Invalid header: {line}") from exc


def _load_lemma(data: TSVData, pwn_id: str, args: list[str]) -> None:
    offset, pos = _split_offset_pos(pwn_id)
    lemma = _clean_lemma(args[0])
    eid = entry_id(data.lex_id, lemma, pos)
    sid = sense_id(data.lex_id, lemma, offset, pos)
    ssid = synset_id(data.lex_id, offset, pos)
    # create entry if necessary
    if eid not in data.entries:
        data.entries[eid] = EntryData(
            eid,
            pos,
            forms=[Form(writtenForm=lemma, pronunciations=[], tags=[])],
        )
    # establish sense with entry and synset
    sense = Sense(
        id=sid,
        synset=ssid,
        counts=[],
        lexicalized=True,
    )
    data.synsets[pwn_id].members[lemma] = sense
    data.entries[eid].senses[pwn_id] = sense

    data.prev_lemma = lemma  # for checking count or pron lemmas
    data.sense_counts[sid] += 1  # for validation


def _load_lemma_root(data: TSVData, pwn_id: str, args: list[str]) -> None:
    lemma = _clean_lemma(args[0])
    # skip if the same as the primary lemma
    if lemma != data.prev_lemma:
        tags = [Tag(text="root", category="form")]
        _load_wordform_helper(data, pwn_id, lemma, tags=tags)
    else:
        raise TSV2LMFError(
            f"Ignoring root {lemma} ({pwn_id}) which matches the primary lemma"
        )


def _load_lemma_brokenplural(data: TSVData, pwn_id: str, args: list[str]) -> None:
    lemma = _clean_lemma(args[0])
    tags = [Tag(text="plural", category="number")]
    _load_wordform_helper(data, pwn_id, lemma, tags=tags)


def _load_wordform_helper(
    data: TSVData,
    pwn_id: str,
    lemma: str,
    tags: Sequence[Tag] = (),
) -> None:
    _, pos = _split_offset_pos(pwn_id)
    eid = entry_id(data.lex_id, data.prev_lemma, pos)
    if pwn_id != data.prev_pwn_id:
        raise TSV2LMFError(
            f"Wordform {lemma} is not grouped with its synset: "
            f"{pwn_id} != {data.prev_pwn_id}"
        )
    elif eid not in data.entries:
        raise TSV2LMFError(
            f"Cannot add wordform {lemma}; "
            f"lemma is not yet defined for {pwn_id}"
        )
    data.entries[eid].forms.append(Form(writtenForm=lemma, tags=list(tags)))


def _load_count(data: TSVData, pwn_id: str, args: list[str]) -> None:
    lemma = _clean_lemma(args[0])
    _check_lemma(lemma, data.prev_lemma)
    sd = data.synsets[pwn_id]
    sd.members[lemma]["counts"].append(_get_count(args))


def _load_pron(data: TSVData, pwn_id: str, args: list[str]) -> None:
    lemma = _clean_lemma(args[0])
    _check_lemma(lemma, data.prev_lemma)
    eid = entry_id(data.lex_id, lemma, _split_offset_pos(pwn_id)[1])
    last_form = data.entries[eid].forms[-1]
    last_form["pronunciations"].append(_get_pronunciation(args))


def _load_exe(data: TSVData, pwn_id: str, args: list[str]) -> None:
    sd = data.synsets[pwn_id]
    sd.examples.append(_get_exe_or_def(args))


def _load_def(data: TSVData, pwn_id: str, args: list[str]) -> None:
    sd = data.synsets[pwn_id]
    sd.definitions.append(_get_exe_or_def(args))


FUNCTIONS = {
    "lemma": _load_lemma,
    "lemma:root": _load_lemma_root,
    "lemma:brokenplural": _load_lemma_brokenplural,
    "count": _load_count,
    "pron": _load_pron,
    "exe": _load_exe,
    "def": _load_def,
}


def load(
    source: Path,
    lex_id: str,
    abort_on_errors: bool = False
) -> TSVData:
    data = TSVData(lex_id)
    with source.open("rt") as tabfile:
        _load_header(data, next(tabfile))  # reads line 1
        prefix = f"{data.language}:"

        for lineno, line in enumerate(tabfile, 2):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            pwn_id, type_, *args = line.split("\t")
            pwn_id = pwn_id.strip()
            # only match for current language
            type_ = type_.strip().removeprefix(prefix)

            if pwn_id not in data.synsets:
                offset, pos = _split_offset_pos(pwn_id)
                ssid = synset_id(lex_id, offset, pos)
                data.synsets[pwn_id] = SynsetData(ssid, pos)

            try:
                func = FUNCTIONS[type_]
            except KeyError:
                log.warning("Ignoring line %d with unknown type: %s", lineno, line)
            else:
                try:
                    func(data, pwn_id, args)
                except TSV2LMFError as exc:
                    log.error("%s\n  at line %d: %s", str(exc), lineno, line)
                    if abort_on_errors:
                        raise
                else:
                    data.prev_pwn_id = pwn_id

    return data


def _split_offset_pos(offset_pos: str) -> tuple[str, str]:
    offset, _, pos = offset_pos.rpartition("-")
    if pos == "s":
        pos = "a"  # no satellite adjectives in OMW
    return offset, pos


def _clean_lemma(lemma: str) -> str:
    lemma = lemma.strip()
    if lemma.startswith('"') and lemma.endswith('"'):
        lemma = lemma[1:-1]
        log.info("CLEANED: %s (removed start and end double quote)", lemma)
    if '"' in lemma:
        log.warning("%s (contains a double quote)", lemma)
    lemma = lemma.replace("_", " ")
    return lemma


def _check_lemma(current: str, previous: str) -> None:
    if current != previous:
        raise TSV2LMFError(f"Lemma doesn't match previous: {current} != {previous}")


def _get_count(args: list[str]) -> Count:
    try:
        value = int(args[1].strip())
    except (IndexError, ValueError) as exc:
        raise TSV2LMFError(f"Missing or invalid count: {args}") from exc
    return Count(value=value)


def _get_pronunciation(args: list[str]) -> Pronunciation:
    padding = [""] * 3  # in case missing values were stripped
    try:
        text, variety, audio, notation, *_ = *args[1:], *padding
    except ValueError as exc:
        raise TSV2LMFError(f"Missing pronunciation: {args}") from exc
    return Pronunciation(
        text=text.strip(),
        variety=variety.strip(),
        notation=notation.strip(),
        audio=audio.strip(),
    )


def _get_exe_or_def(args: list[str]) -> tuple[int, str]:
    try:
        order_, text = args
        order = int(order_)
    except ValueError as exc:
        raise TSV2LMFError(f"Invalid example/definition: {args}") from exc
    return order, text.strip()


# TRANSFORMATION #######################################################

LEXICAL_GAP_INDICATORS = [
    "GAP!",
    "PSEUDOGAP!",
]


def process_lexical_gaps(data: TSVData) -> None:
    for pwn_id, sd in data.synsets.items():
        for indicator in LEXICAL_GAP_INDICATORS:
            if indicator in sd.members:
                log.info("Updating lexicalized status on %s senses", pwn_id)
                del sd.members[indicator]
                for lemma, sense in sd.members.items():
                    _update_lexicalized(sense, lemma, data.language)
        # if all senses are lexicalized or there are no senses, then
        # the synset gets marked with lexicalized=False
        if all(not sense["lexicalized"] for sense in sd.members.values()):
            sd.lexicalized = False
    # finally remove the lexical entries for the gap indicators
    for pos in "nvar":
        for indicator in LEXICAL_GAP_INDICATORS:
            eid = entry_id(data.lex_id, indicator, pos)
            if eid in data.entries:
                del data.entries[eid]


def _update_lexicalized(sense: Sense, lemma: str, lang: str) -> None:
    # currently assuming 2 things:
    #  * the language uses spaces to delimit words (plus ' for italian)
    #  * multiple words implies a lexical gap
    if lang == "ita":
        if " " in lemma or "'" in lemma:
            sense["lexicalized"] = False
    elif lang == "heb":
        if " " in lemma:
            sense["lexicalized"] = False
    else:
        log.warning("No lexicalization rules encoded for [%s]", lang)


# VALIDATION ###########################################################


def validate(lex: Lexicon, data: TSVData) -> None:
    if data.language not in BCP47:
        log.warning("UNKNOWN LANGUAGE: %s", data.language)
    elif BCP47[data.language] != lex["language"]:
        log.warning(
            "INDEX INCONSISTENT WITH SOURCE: %s != %s",
            BCP47[data.language],
            lex["language"],
        )
    if data.license not in OPEN_LICENSES:
        log.warning("UNKNOWN LICENSE: %s", data.license)
    elif OPEN_LICENSES[data.license] != lex["license"]:
        log.warning(
            "INDEX INCONSISTENT WITH SOURCE: %s != %s",
            OPEN_LICENSES[data.license],
            lex["license"],
        )

    redundant_senses = data.sense_counts - Counter(set(data.sense_counts))
    for sid, count in redundant_senses.items():
        log.warning("REDUNDANT SENSES SUPPRESSED: %s (%d occurrences)", sid, count)

    for sd in data.synsets.values():
        if len(sd.members) == 0 and sd.lexicalized:
            log.warning("EMPTY SYNSET: %s", sd.id)


# LEXICON BUILDING #####################################################


def build(
    lex: Lexicon,
    data: TSVData,
    ilimap: dict[str, str],
) -> None:
    for ed in data.entries.values():
        lemma_form = ed.forms[0]
        lex["entries"].append(
            LexicalEntry(
                id=ed.id,
                lemma=Lemma(
                    writtenForm=lemma_form["writtenForm"],
                    partOfSpeech=ed.pos,
                    pronunciations=lemma_form["pronunciations"],
                    tags=lemma_form["tags"],
                ),
                forms=ed.forms[1:],
                senses=list(ed.senses.values()),
            )
        )
    for pwn_id, sd in data.synsets.items():
        lex["synsets"].append(
            Synset(
                id=sd.id,
                ili=ilimap.get(pwn_id, ""),
                partOfSpeech=sd.pos,
                definitions=[
                    Definition(text=defn) for _, defn in sorted(sd.definitions)
                ],
                examples=[Example(text=ex) for _, ex in sorted(sd.examples)],
                lexicalized=sd.lexicalized,
                members=[sense["id"] for sense in sd.members.values()],
            )
        )


# ID FORMATTERS ########################################################


def synset_id(lexid: str, offset: str, pos: str) -> str:
    return f"{lexid}-{offset}-{pos}"


def entry_id(lexid: str, lemma: str, pos: str) -> str:
    return f"{lexid}-{escape_lemma(lemma)}-{pos}"


def sense_id(lexid: str, lemma: str, offset: str, pos: str) -> str:
    return f"{lexid}-{escape_lemma(lemma)}-{offset}-{pos}"


# COMMAND-LINE INTERFACE ###############################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("SOURCE", help="source TSV file")
    parser.add_argument("DESTINATION", help="output XML file path")
    parser.add_argument("--id", required=True, help="lexicon ID")
    parser.add_argument("--label", required=True, help="name or description")
    parser.add_argument("--language", required=True, help="language (BCP-47)")
    parser.add_argument("--email", required=True, help="project email address")
    parser.add_argument("--license", required=True, help="license name or URL")
    parser.add_argument("--version", required=True, help="lexicon version")
    parser.add_argument("--url", help="project url")
    parser.add_argument("--citation", help="readable citation")
    parser.add_argument("--logo", help="url of project logo")
    parser.add_argument("--requires", metavar="ID:VERSION", help="lexicon dependency")
    parser.add_argument(
        "--meta",
        action="append",
        metavar="KEY=VALUE",
        help="lexicon metadata; may be repeated",
    )
    parser.add_argument("--ili-map", metavar="PATH", help="synset to ILI mapping file")
    parser.add_argument(
        "--log",
        type=Path,
        metavar="PATH",
        help="file for logging output (default: stderr)",
    )
    parser.add_argument(
        "--abort-on-errors",
        action="store_true",
        help="reraise TSV2LMFErrors and stop immediately",
    )
    args = parser.parse_args()

    sys.exit(main(args))
