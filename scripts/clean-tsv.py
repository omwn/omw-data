import argparse
import datetime
import sys
from contextlib import nullcontext
from pathlib import Path

from .util import load_tsv, strip_quotes


def main(args: argparse.Namespace) -> int:
    header, rows = load_tsv(args.TSVFILE)

    seen_lemmas: dict[str, set[tuple[str, str]]] = {}

    if args.in_place:
        tabfile = args.TSVFILE.open("wt", encoding="utf-8")
    else:
        tabfile = nullcontext(sys.stdout)  # so we can use `with tabfile:`

    date = datetime.date.today().isoformat()  # for the log
    logfile = nullcontext(sys.stderr)

    with tabfile as out, logfile as err:
        print(header, file=out)

        for row in rows:
            offset_pos, row_type, text, order = row

            lemma_set = seen_lemmas.setdefault(offset_pos, set())
            if row.is_lemma():
                lemma = text.replace("_", " ")  # Use actual spaces
                lemma = lemma.strip()  # strip spaces to help quote-stripping
                lemma = strip_quotes(lemma)

                lemma_type = "" if args.ignore_lemma_type else row_type

                key = (lemma, lemma_type)
                original = "\t".join(row[:3])
                if lemma and key not in lemma_set:
                    if lemma != text:
                        print(f"{date}\tMODIFIED\t{original}\t{lemma}", file=err)
                    print(f"{offset_pos}\t{row_type}\t{lemma}", file=out)
                    lemma_set.add(key)
                else:
                    print(f"{date}\tREMOVED\t{original}", file=err)

            elif row_type.endswith((":def", "exe")):
                entry = f"{offset_pos}\t{row_type}\t{order}\t{text}"
                if text.strip():
                    print(entry, file=out)
                else:
                    print(f"{date}\tREMOVED\t{entry}", file=err)

            else:
                raise Exception(f"unexpected row type: {row_type}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove duplicate lemmas and strip quotes from TSV files.",
        epilog=(
            "WARNING: --in-place modifies the original TSVFILE! It is suggested "
            "that you work with a file checked into version control so you can "
            "inspect the diffs and revert if necessary."
        ),
    )
    parser.add_argument("TSVFILE", type=Path, help="path to TSV file")
    parser.add_argument(
        "--ignore-lemma-type",
        action="store_true",
        help="don't consider the lemma type column in deduping",
    )
    parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="modify the original file instead of writing to stdout",
    )
    args = parser.parse_args()
    sys.exit(main(args))
