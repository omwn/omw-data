import argparse
from collections import defaultdict
import csv
import logging
from pathlib import Path
import sys
import tempfile
from typing import Tuple
from unicodedata import normalize, combining


logger = logging.getLogger('tsv-duplicates')

Entry = Tuple[str, str, str]


def normalize_lemma(s: str, args: argparse.Namespace) -> str:
    norm = s
    if args.ignore_case:
        norm = norm.lower()
    if args.underscore:
        norm = norm.replace('_', ' ')
    if args.diacritics:
        norm = ''.join(c for c in normalize('NFKD', norm) if not combining(c))
    return norm


def load_tsv(path: Path) -> tuple[str, list[Entry]]:
    with path.open(newline='') as csvfile:
        reader = csv.reader(csvfile, dialect='excel-tab', quoting=csv.QUOTE_NONE)
        header = next(reader)
        entries: list[Entry] = []
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            if row[1].endswith("lemma"):
                assert len(row) == 3, f"unexpected number of columns: {row}"
                entries.append((row[0], row[1], row[2]))
    return header, entries


def check_duplicates(path: Path, args: argparse.Namespace) -> int:
    header, entries = load_tsv(path)
    seen: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for off_pos, _, lemma in entries:
        seen[off_pos][normalize_lemma(lemma, args)].append(lemma)

    synset_count = 0
    lemma_count = 0
    for off_pos, lemma_groups in seen.items():
        for norm, lemmas in lemma_groups.items():
            if len(lemmas) > 1:
                synset_count += 1
                lemma_count += len(lemmas)
                logger.warning(
                    f"duplicate of {off_pos}: " + ", ".join(map(repr, lemmas))
                )

    return synset_count, lemma_count


def main(args: argparse.Namespace) -> int:
    retcode = 0

    synset_total = lemma_total = 0
    for path in args.TSV:
        synset_count, lemma_count = check_duplicates(path, args)
        if synset_count or lemma_count:
            print(
                f"{path.name} duplicates"
                f"\t{synset_count} synsets"
                f"\t{lemma_count} lemmas"
            )
            synset_total += synset_count
            lemma_total += lemma_count
            retcode = 1

    print(f"total duplicates\t{synset_total} synsets\t{lemma_total} lemmas")

    return retcode


parser = argparse.ArgumentParser()
parser.add_argument("TSV", nargs='+', type=Path, help="path to TSV file")
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='log warnings for each item',
)
parser.add_argument(
    '-i',
    '--ignore-case',
    action='store_true',
    help='ignore case distinctions in lemmas',
)
parser.add_argument(
    '-u',
    '--underscore',
    action='store_true',
    help='treat underscores as spaces in lemmas',
)
parser.add_argument(
    '-d',
    '--diacritics',
    action='store_true',
    help='ignore diacritics with NFKD normalization',
)
args = parser.parse_args()
logging.basicConfig(level=logging.WARNING if args.verbose else logging.ERROR)

sys.exit(main(args))
