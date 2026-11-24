"""Shared A24 metadata loaders (no screenplay text)."""

from __future__ import annotations

import csv
import re
import urllib.request
from pathlib import Path

ALEXPMORTON_RELEASED_CSV = (
    "https://raw.githubusercontent.com/AlexPMorton/A24-Movies-EDA/master/"
    "A24%20Released%20Movies/A24_Released_Movies_2022_09_26.csv"
)
ALEXPMORTON_OSCARS_CSV = (
    "https://raw.githubusercontent.com/AlexPMorton/A24-Movies-EDA/master/"
    "A24%20Oscars/a24_released_movies_and_oscars.csv"
)

KAGGLE_METADATA_SLUGS: dict[str, str] = {
    "sebastiansuliborski/a24-studio-movies-dataset": "a24_data_cleaned.csv",
    "dvdlws/a24-movie-database": "A24 Dataset.csv",
    "alsyab/a24-films": "a24films_movies.csv",
}

DEFAULT_KAGGLE_SLUG = "sebastiansuliborski/a24-studio-movies-dataset"


def slug_title(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "_", s)


def script_slug_guess_path(title: str, year: str) -> str | None:
    """Human hint for manual Script Slug lookup — not verified against the site."""
    if not title:
        return None
    base = re.sub(r"[^\w\s-]", "", title.strip().lower())
    base = re.sub(r"\s+", "-", base)
    if year:
        return f"/script/{base}-{year}"
    return f"/script/{base}"


def fetch_csv_url(url: str) -> list[dict[str, str]]:
    with urllib.request.urlopen(url, timeout=60) as resp:
        text = resp.read().decode("utf-8-sig", errors="replace")
    return list(csv.DictReader(text.splitlines()))


def rows_from_alexp_morton(url: str, source_label: str = "AlexPMorton/A24-Movies-EDA") -> list[dict]:
    rows = fetch_csv_url(url)
    out: list[dict] = []
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
        out.append(
            {
                "title": title,
                "title_slug": slug_title(title),
                "release_year": year,
                "director": (row.get("director") or "").strip(),
                "genre": (row.get("genre") or "").strip(),
                "source": source_label,
                "script_slug_path_guess": script_slug_guess_path(title, year),
                "cole_haddon_60_a24": None,
            }
        )
    return out


def rows_from_local_csv(path: Path, source_label: str) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.DictReader(handle)
        out: list[dict] = []
        for row in reader:
            title = (row.get("title") or row.get("Title") or row.get("name") or "").strip()
            if not title:
                continue
            year = (row.get("release_year") or row.get("year") or row.get("Year") or "").strip()
            if not year:
                rd = row.get("release_date") or row.get("Release dates") or ""
                m = re.search(r"(\d{4})", str(rd))
                year = m.group(1) if m else ""
            out.append(
                {
                    "title": title,
                    "title_slug": slug_title(title),
                    "release_year": year,
                    "director": (row.get("director") or row.get("Directed by") or "").strip(),
                    "genre": (row.get("genre") or "").strip(),
                    "source": source_label,
                    "script_slug_path_guess": script_slug_guess_path(title, year),
                    "cole_haddon_60_a24": None,
                }
            )
        return out


def write_titles_csv(rows: list[dict], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "title",
        "title_slug",
        "release_year",
        "director",
        "genre",
        "source",
    ]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r.get("release_year") or "", r["title"])):
            writer.writerow({k: row.get(k, "") for k in fieldnames})