"""Export A24 title index (CSV). Prefer scrape_a24_metadata.py for JSON + index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from a24_metadata_lib import (  # noqa: E402
    ALEXPMORTON_OSCARS_CSV,
    ALEXPMORTON_RELEASED_CSV,
    KAGGLE_METADATA_SLUGS,
    rows_from_alexp_morton,
    rows_from_local_csv,
    write_titles_csv,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "ingest" / "a24_titles.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build data/ingest/a24_titles.csv from public A24 metadata (no scripts)."
    )
    parser.add_argument(
        "--source",
        choices=("github-alexp", "github-alexp-oscars", "local"),
        default="github-alexp",
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--input-label", default="local-csv")
    parser.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.source == "github-alexp":
        rows = rows_from_alexp_morton(ALEXPMORTON_RELEASED_CSV)
    elif args.source == "github-alexp-oscars":
        rows = rows_from_alexp_morton(ALEXPMORTON_OSCARS_CSV)
    else:
        if not args.input or not args.input.exists():
            slugs = ", ".join(KAGGLE_METADATA_SLUGS)
            raise SystemExit(f"--source local requires --input. Kaggle slugs: {slugs}")
        rows = rows_from_local_csv(args.input, args.input_label)

    write_titles_csv(rows, args.out)
    print(f"Wrote {len(rows)} titles to {args.out}")
    print("For JSON + Script Slug index stubs: python3 scripts/scrape_a24_metadata.py")


if __name__ == "__main__":
    main()