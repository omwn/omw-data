import argparse
import logging
import sys
from functools import partial
from itertools import groupby
from pathlib import Path
from typing import Callable
from unicodedata import normalize, combining

from .util import load_tsv, strip_quotes

logger = logging.getLogger("tsv-duplicates")


def make_normalizer(args: argparse.Namespace) -> Callable[[str], str]:

    def normalize_lemma(s: str) -> str:
        norm = s
        if args.ignore_case:
            norm = norm.lower()
        if args.underscore:
            norm = norm.replace("_", " ")
        if args.diacritics:
            norm = "".join(c for c in normalize("NFKD", norm) if not combining(c))
        if args.quotes:
            norm = strip_quotes(norm.strip())
        return norm

    return normalize_lemma


def check_duplicates(
    offset_pos: str,
    lemmas: list[str],
    normalizer: Callable[[str], str],
    label: str,
    verbose: bool,
) -> int:
    _sorted = sorted(lemmas, key=normalizer)
    count = 0
    for _, grp in groupby(_sorted, key=normalizer):
        dupes = list(grp)
        if len(dupes) > 1:
            if verbose:
                print(f"\t{offset_pos}\texact\t{'; '.join(dupes)}")
            count += len(dupes) - 1
    return count


def check_polysemy(
    data: dict[str, list[str]],
    polysemy_threshold: int,
    verbose: bool,
) -> int:
    # map lemmas to synsets
    _data: dict[str, list[str]] = {}
    for offset_pos, lemmas in data.items():
        for lemma in set(lemmas):
            _data.setdefault(lemma, []).append(offset_pos)
    polysem_count = 0
    for lemma, offsets in _data.items():
        if len(offsets) >= polysemy_threshold:
            if verbose:
                print(f"\t{lemma}\tpolysem\t{'; '.join(offsets)}")
            polysem_count += 1
    return polysem_count


def load_data(path: Path) -> dict[str, list[str]]:
    data: dict[str, list[str]] = {}
    _, rows = load_tsv(path)
    for row in rows:
        if not row.is_lemma():
            continue
        data.setdefault(row.offset_pos, []).append(row.text)
    return data


def main(args: argparse.Namespace) -> int:
    retcode = 0

    check_exact = partial(
        check_duplicates,
        normalizer=str,
        label="exact",
        verbose=args.verbose,
    )
    check_normalized = partial(
        check_duplicates,
        normalizer=make_normalizer(args),
        label="".join([
            "i" if args.ignore_case else "",
            "u" if args.underscore else "",
            "d" if args.diacritics else "",
            "q" if args.quotes else "",
        ]),
        verbose=args.verbose,
    )

    for path in args.TSV:
        print(f"Checking for duplicates in {path}")
        data = load_data(path)

        synsets: set[str] = set()
        lemma_count = 0
        for offset_pos, lemmas in data.items():
            # exact duplicates
            if cnt := check_exact(offset_pos, lemmas):
                synsets.add(offset_pos)
                lemma_count += cnt
            # normalized duplicates minus exact duplicates
            if cnt := check_normalized(offset_pos, set(lemmas)):
                synsets.add(offset_pos)
                lemma_count += cnt
        print(f"  Synsets with redundant lemmas: {len(synsets)}")
        print(f"  Total count of redundant lemmas: {lemma_count}")

        if args.polysemy_threshold:
            polysem_count = check_polysemy(data, args.polysemy_threshold, args.verbose)
            print(f"  Lemmas with > {args.polysemy_threshold} senses: {polysem_count}")

    return retcode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("TSV", nargs="+", type=Path, help="path to TSV file")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="log warnings for each item",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="ignore case distinctions in lemmas",
    )
    parser.add_argument(
        "-u",
        "--underscore",
        action="store_true",
        help="treat underscores as spaces in lemmas",
    )
    parser.add_argument(
        "-d",
        "--diacritics",
        action="store_true",
        help="ignore diacritics with NFKD normalization",
    )
    parser.add_argument(
        "-q",
        "--quotes",
        action="store_true",
        help="strip quote pairs from start/end of lemmas",
    )
    parser.add_argument(
        "-p",
        "--polysemy-threshold",
        type=int,
        metavar="N",
        help="report lemmas that are used in N (>=2) or more synsets",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING if args.verbose else logging.ERROR)

    sys.exit(main(args))
