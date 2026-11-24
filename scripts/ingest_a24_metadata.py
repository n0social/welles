"""Export a committed A24 title index for script-tier join keys (metadata only).

No screenplay text. Sources are documented in data/ingest/kaggle_sources.md
(AlexPMorton GitHub CSV, Kaggle catalog CSVs). This script does not scrape
Script Slug, Cole Haddon links, or PDF hosts.
"""

from __future__ import annotations

import argparse
import csv
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "ingest" / "a24_titles.csv"

# Public metadata snapshot (Sept 2022); no script bodies.
ALEXPMORTON_RELEASED_CSV = (
    "https://raw.githubusercontent.com/AlexPMorton/A24-Movies-EDA/master/"
    "A24%20Released%20Movies/A24_Released_Movies_2022_09_26.csv"
)
ALEXPMORTON_OSCARS_CSV = (
    "https://raw.githubusercontent.com/AlexPMorton/A24-Movies-EDA/master/"
    "A24%20Oscars/a24_released_movies_and_oscars.csv"
)

# Kaggle alternatives (manual `kaggle datasets download` — not wired to API here):
KAGGLE_METADATA_SLUGS = {
    "sebastiansuliborski/a24-studio-movies-dataset": "a24_data_cleaned.csv",
    "dvdlws/a24-movie-database": "A24 Dataset.csv",
    "alsyab/a24-films": "a24films_movies.csv",
}


def _slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "_", s)


def _fetch_csv(url: str) -> list[dict[str, str]]:
    with urllib.request.urlopen(url, timeout=60) as resp:
        text = resp.read().decode("utf-8-sig", errors="replace")
    return list(csv.DictReader(text.splitlines()))


def rows_from_alexp_morton(source: str) -> list[dict[str, str]]:
    rows = _fetch_csv(source)
    out: list[dict[str, str]] = []
    for row in rows:
        title = (row.get("title") or "").strip()
        if not title:
            continue
        release = (row.get("release_date") or "").strip()
        year = ""
        if release:
            m = re.search(r"(\d{4})", release)
            if m:
                year = m.group(1)
        director = (row.get("director") or "").strip()
        genre = (row.get("genre") or "").strip()
        out.append(
            {
                "title": title,
                "title_slug": _slug(title),
                "release_year": year,
                "director": director,
                "genre": genre,
                "source": "AlexPMorton/A24-Movies-EDA",
            }
        )
    return out


def rows_from_local(path: Path, source_label: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.DictReader(handle)
        out: list[dict[str, str]] = []
        for row in reader:
            title = (row.get("title") or row.get("Title") or row.get("name") or "").strip()
            if not title:
                continue
            year = (
                (row.get("release_year") or row.get("year") or row.get("Year") or "")
                .strip()
            )
            if not year:
                rd = row.get("release_date") or row.get("Release dates") or ""
                m = re.search(r"(\d{4})", rd)
                year = m.group(1) if m else ""
            director = (row.get("director") or row.get("Directed by") or "").strip()
            genre = (row.get("genre") or "").strip()
            out.append(
                {
                    "title": title,
                    "title_slug": _slug(title),
                    "release_year": year,
                    "director": director,
                    "genre": genre,
                    "source": source_label,
                }
            )
        return out


def write_csv(rows: list[dict[str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["title", "title_slug", "release_year", "director", "genre", "source"]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r.get("release_year") or "", r["title"])):
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build data/ingest/a24_titles.csv from public A24 metadata (no scripts)."
    )
    parser.add_argument(
        "--source",
        choices=("github-alexp", "github-alexp-oscars", "local"),
        default="github-alexp",
        help="Metadata provenance (default: AlexPMorton released-movies CSV on GitHub).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Local CSV path when --source local (e.g. after kaggle datasets download).",
    )
    parser.add_argument(
        "--input-label",
        default="local-csv",
        help="Value for source column when using --source local.",
    )
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
            raise SystemExit(
                f"--source local requires --input. Download a Kaggle metadata CSV first "
                f"({slugs})"
            )
        rows = rows_from_local(args.input, args.input_label)

    write_csv(rows, args.out)
    print(f"Wrote {len(rows)} titles to {args.out}")


if __name__ == "__main__":
    main()