import argparse
import sys
from pathlib import Path

from .util import load_tsv, strip_quotes


def main(args: argparse.Namespace) -> int:
    header, rows = load_tsv(args.TSVFILE)

    seen_lemmas: dict[str, set[str]] = {}
    with args.TSVFILE.open("wt", encoding="utf-8") as tabfile:
        print(header, file=tabfile)

        for row in rows:
            offset_pos, row_type, text, order = row

            lemma_set = seen_lemmas.setdefault(offset_pos, set())
            if row.is_lemma():
                text = text.replace("_", " ")  # Use actual spaces
                text = text.strip()  # strip spaces to help quote-stripping
                lemma = strip_quotes(text)
                if lemma not in lemma_set:
                    print(f"{offset_pos}\t{row_type}\t{lemma}", file=tabfile)
                    lemma_set.add(lemma)

            elif row_type.endswith((":def", "exe")):
                print(f"{offset_pos}\t{row_type}\t{order}\t{text}", file=tabfile)

            else:
                raise Exception(f"unexpected row type: {row_type}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove duplicate lemmas and strip quotes from TSV files.",
        epilog=(
            "WARNING: This modifies the original TSVFILE! It is suggested that you "
            "work with a file checked into version control so you can inspect the "
            "diffs and revert if necessary."
        ),
    )
    parser.add_argument("TSVFILE", type=Path, help="path to TSV file")
    args = parser.parse_args()
    sys.exit(main(args))
