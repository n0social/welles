"""Refresh Orson Welles directed-feature metadata (titles only — no scripts).

Embeds the canonical filmography from `data/ingest/script_sources.md` and writes:
  - data/ingest/welles_titles.json
  - data/ingest/welles_script_slug_index.json (URL guesses + public study links)

No HTTP scrape of IMSDb, Script Slug, or screenplay hosts.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from a24_metadata_lib import script_slug_guess_path, slug_title  # noqa: E402

TITLES_JSON = ROOT / "data" / "ingest" / "welles_titles.json"
INDEX_JSON = ROOT / "data" / "ingest" / "welles_script_slug_index.json"
IMSDB_WRITER = "https://imsdb.com/writer.php?w=Orson+Welles"
WELLESNET_SCRIPTS = "https://wellesnet.com/unfilmed-orson-welles-scripts-available-online/"
UIUC_KANE = (
    "https://digital.library.illinois.edu/items/"
    "fb1e7c00-6ae8-0137-6d00-02d0d7bfd6e4-9"
)

# Canonical Orson Welles director credits (feature / notable shorts)
FILMOGRAPHY: list[dict[str, str]] = [
    {"title": "Too Much Johnson", "release_year": "1938", "note": "unfinished"},
    {"title": "Citizen Kane", "release_year": "1941"},
    {"title": "The Magnificent Ambersons", "release_year": "1942"},
    {"title": "Journey into Fear", "release_year": "1943", "note": "co-directed"},
    {"title": "The Stranger", "release_year": "1946"},
    {"title": "The Lady from Shanghai", "release_year": "1947"},
    {"title": "Macbeth", "release_year": "1948"},
    {"title": "Othello", "release_year": "1952"},
    {"title": "Mr. Arkadin", "release_year": "1955"},
    {"title": "Touch of Evil", "release_year": "1958"},
    {"title": "The Trial", "release_year": "1962"},
    {"title": "Chimes at Midnight", "release_year": "1965"},
    {"title": "The Immortal Story", "release_year": "1968"},
    {"title": "F for Fake", "release_year": "1973"},
    {"title": "Filming Othello", "release_year": "1978"},
    {"title": "The Other Side of the Wind", "release_year": "2018", "note": "posthumous"},
]


def utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def study_links(title: str, year: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = [
        {"label": "IMSDb writer index", "url": IMSDB_WRITER},
    ]
    if title == "Citizen Kane" and year == "1941":
        links.insert(
            0,
            {
                "label": "UIUC Digital Collections (surrogate)",
                "url": UIUC_KANE,
                "note": "In Copyright — research surrogate only.",
            },
        )
    if title in ("The Other Side of the Wind", "Too Much Johnson"):
        links.append({"label": "Wellesnet script pointers", "url": WELLESNET_SCRIPTS})
    return links


def build_titles_doc() -> dict:
    titles = []
    for row in FILMOGRAPHY:
        title = row["title"]
        year = row["release_year"]
        titles.append(
            {
                "title": title,
                "release_year": year,
                "title_slug": slug_title(title),
                "director_credit": "Orson Welles",
                **({"note": row["note"]} if row.get("note") else {}),
            }
        )
    return {
        "survey_date": utc_date(),
        "provenance": "Embedded filmography from script_sources.md (no live scrape)",
        "automated_scrape_performed": False,
        "titles": titles,
    }


def build_index_doc(titles: list[dict]) -> dict:
    entries = []
    for row in titles:
        title = row["title"]
        year = str(row.get("release_year") or "")
        path_guess = script_slug_guess_path(title, year)
        slug_url = f"https://www.scriptslug.com{path_guess}" if path_guess else None
        entries.append(
            {
                "title": title,
                "release_year": year,
                "title_slug": row.get("title_slug") or slug_title(title),
                "script_slug_url": slug_url,
                "script_slug_url_verified": False,
                "study_links": study_links(title, year),
                "moviesum_hf_key_guess": f"{title}_{year}",
            }
        )
    return {
        "survey_date": utc_date(),
        "automated_scrape_performed": False,
        "legal_note": "URLs are manual-study hints only. No script bodies are fetched or committed.",
        "imsdb_writer_index": IMSDB_WRITER,
        "script_slug_policy": {
            "url_pattern_note": "https://www.scriptslug.com/script/{kebab-title}-{year}",
            "reason_no_scrape": "Script Slug ToS forbids automated scraping; many Welles titles lack studio listings.",
        },
        "entries": entries,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Welles filmography JSON (metadata only).")
    p.add_argument("--titles-out", type=Path, default=TITLES_JSON)
    p.add_argument("--index-out", type=Path, default=INDEX_JSON)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    titles_doc = build_titles_doc()
    index_doc = build_index_doc(titles_doc["titles"])
    print(f"Titles: {len(titles_doc['titles'])} | Index entries: {len(index_doc['entries'])}")
    if args.dry_run:
        return
    args.titles_out.parent.mkdir(parents=True, exist_ok=True)
    args.titles_out.write_text(json.dumps(titles_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.index_out.write_text(json.dumps(index_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.titles_out}\nWrote {args.index_out}")


if __name__ == "__main__":
    main()