### summarize the release

import argparse
import logging
import sys
from functools import partial
from pathlib import Path

from wn import lmf
from wn.project import iterpackages

log = logging.getLogger("summarize-release")

FRIENDLY_LICENSE_NAME_MAP = {
    "wordnet": "wordnet",
    "https://wordnet.princeton.edu/license-and-commercial-use": "WordNet",
    "WordNet-1.5 License": "WordNet",
    "WordNet-1.6 License": "WordNet",
    "https://wordnetcode.princeton.edu/1.7/LICENSE": "WordNet",
    "https://wordnetcode.princeton.edu/1.7.1/LICENSE": "WordNet",
    "https://wordnetcode.princeton.edu/2.0/LICENSE": "WordNet",
    "https://wordnetcode.princeton.edu/2.1/LICENSE": "WordNet",
    "http://opendefinition.org/licenses/odc-by/": "ODC-BY",
    "http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html": "CeCILL-1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0-1.0",
    "https://creativecommons.org/licenses/by/": "CC-BY",
    "https://creativecommons.org/licenses/by-sa/": "CC-BY-SA",
    "https://creativecommons.org/licenses/by/3.0/": "CC-BY-3.0",
    "https://creativecommons.org/licenses/by-sa/3.0/": "CC-BY-SA 3.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC-BY-4.0",
    "https://creativecommons.org/licenses/by-sa/4.0/": "CC-BY-SA 4.0",
    "https://creativecommons.org/licenses/by-nc-sa/4.0/": "CC-BY-NC-SA 4.0",
    "https://opensource.org/licenses/MIT/": "MIT",
    "https://opensource.org/licenses/Apache-2.0": "Apache-2.0",
    "https://www.unicode.org/license.html": "unicode"
}


def main(args: argparse.Namespace) -> int:
    fields = [
        _identifier,  # this should always be first
        _language,
        _label,
        _license,
        _synsets,
        _senses,
        _words,
    ]

    if args.core_ili:
        core = _load_core_ili(args.core_ili)
        core_func = partial(_core, core=core)
        core_func.__doc__ = _core.__doc__  # docstring is for table formatting
        fields.append(core_func)
    else:
        core = set()

    log.info("Summarizing release at %s", args.DIR)

    col_infos = [_get_col_info(f.__doc__) for f in fields]

    rows: list[list[str]] = []
    for pkg in iterpackages(args.DIR):
        log.info("Loading %s", pkg.resource_file())
        lex = _load_lexicon(pkg.resource_file())
        rows.append([field_func(lex) for field_func in fields])

    print("|", " | ".join(name for name, _ in col_infos), "|")  # header
    print("|", " | ".join(delim for _, delim in col_infos), "|")  # delimiter
    for row in sorted(rows, key=lambda row: row[0].split(":")[0]):
        print("|", " | ".join(row), "|")

    return 0  # success


def _get_col_info(docstring: str) -> tuple[str, str]:
    name, _, delim = docstring.partition("|")
    return name.strip(), delim.strip()


def _load_core_ili(path: Path) -> set[str]:
    core = set()
    for line in path.open():
        core.add(line.split("\t")[0].strip())
    log.info("%d items loaded from core ILI file at %s", len(core), path)
    return core


def _load_lexicon(path: Path) -> lmf.Lexicon:
    lex_resource = lmf.load(path, progress_handler=None)
    if (count := len(lex_resource["lexicons"])) != 1:
        logging.warning(
            "Unexpected number of lexicons (%d) in resource at %s",
            count,
            path,
        )
    return lex_resource["lexicons"][0]


def _link(text, url):
    if url:
        return f"[{text}]({url})"
    else:
        return text


# The following are the functions computing the values for each column
# of the summary. They should return a string. The docstring is the
# column header followed by a pipe and a markdown table delimiter.

def _identifier(lex: lmf.Lexicon) -> str:
    """ID:ver|------"""
    return f"{lex['id']}:{lex['version']}"


def _language(lex: lmf.Lexicon) -> str:
    """Lang|----"""
    return lex["language"]


def _label(lex: lmf.Lexicon) -> str:
    """Label|-----"""
    return _link(lex["label"], lex.get("url", ""))


def _license(lex: lmf.Lexicon) -> str:
    """License|-------"""
    license = lex["license"]
    license_name = FRIENDLY_LICENSE_NAME_MAP.get(license, license)
    if license.startswith("http"):
        return _link(license_name, license)
    else:
        return license_name


def _synsets(lex: lmf.Lexicon) -> str:
    """Synsets|------:"""
    return str(len(lex["synsets"]))


def _senses(lex: lmf.Lexicon) -> str:
    """Senses|-----:"""
    return str(sum(len(entry["senses"]) for entry in lex["entries"]))


def _words(lex: lmf.Lexicon) -> str:
    """Words|----:"""
    return str(len(lex["entries"]))


def _core(lex: lmf.Lexicon, core: set[str]) -> str:
    """Core|---:"""
    incore = sum(1 for ss in lex["synsets"] if ss["ili"] in core)
    return f"{incore/len(core):.1%}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize the OMW release")
    parser.add_argument("DIR", type=Path, help="the release build directory")
    parser.add_argument(
        "--core-ili",
        type=Path,
        metavar="PATH",
        help="compute percentage of core synsets covered using core ILI file at PATH"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
