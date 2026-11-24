"""Fetch A24 film metadata for title joins (no scripts, no Script Slug scrape).

Order: local --input, optional Kaggle CLI download, then GitHub AlexPMorton CSV.
Outputs data/ingest/a24_titles.json (+ optional CSV).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from a24_metadata_lib import (  # noqa: E402
    ALEXPMORTON_OSCARS_CSV,
    ALEXPMORTON_RELEASED_CSV,
    DEFAULT_KAGGLE_SLUG,
    KAGGLE_METADATA_SLUGS,
    rows_from_alexp_morton,
    rows_from_local_csv,
    write_titles_csv,
)

DEFAULT_JSON = ROOT / "data" / "ingest" / "a24_titles.json"
DEFAULT_CSV = ROOT / "data" / "ingest" / "a24_titles.csv"
INDEX_JSON = ROOT / "data" / "ingest" / "a24_script_slug_index.json"


def kaggle_credentials_present() -> bool:
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    return (Path.home() / ".kaggle" / "kaggle.json").exists()


def download_kaggle_file(slug: str, filename: str, dest_dir: Path) -> Path | None:
    """One Kaggle file via CLI; respects site ToS (metadata datasets only)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not shutil.which("kaggle"):
        return None
    if not kaggle_credentials_present():
        return None
    before = set(dest_dir.iterdir())
    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        slug,
        "-f",
        filename,
        "-p",
        str(dest_dir),
        "--force",
    ]
    subprocess.run(cmd, check=False, capture_output=True, text=True)
    after = set(dest_dir.iterdir()) - before
    for path in after:
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as zf:
                zf.extractall(dest_dir)
        if path.name == filename or (dest_dir / filename).exists():
            return dest_dir / filename
    candidate = dest_dir / filename
    return candidate if candidate.exists() else None


def build_script_slug_index(rows: list[dict]) -> dict:
    return {
        "survey_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "automated_scrape_performed": False,
        "script_slug_policy": {
            "studio_listing": "https://www.scriptslug.com/scripts/studio/a24",
            "url_pattern_note": "https://www.scriptslug.com/script/{kebab-title}-{year}",
            "robots_txt": "https://www.scriptslug.com/robots.txt",
            "ai_policy": "https://www.scriptslug.com/ai.txt",
            "terms": "https://www.scriptslug.com/legal",
            "reason_no_scrape": (
                "Script Slug ToS §9 forbids automated scraping and AI training dataset "
                "creation without written permission; ai.txt denies training rights on PDFs."
            ),
        },
        "cole_haddon": {
            "post_url": "https://colehaddon.substack.com/p/60-a24-screenplays-to-download-and",
            "format": "paid_substack_pdf_links",
            "automated_scrape": False,
            "reason": "Paid Substack; PDF hosts are third-party copyrighted works.",
        },
        "entries": [
            {
                "title": r["title"],
                "release_year": r.get("release_year") or "",
                "title_slug": r["title_slug"],
                "script_slug_url": (
                    f"https://www.scriptslug.com{r['script_slug_path_guess']}"
                    if r.get("script_slug_path_guess")
                    else None
                ),
                "script_slug_url_verified": False,
                "note": "Guessed path for manual browser check only — not fetched by this repo.",
            }
            for r in rows
        ],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect A24 metadata (titles), not screenplays.")
    p.add_argument(
        "--source",
        choices=("auto", "kaggle", "github-alexp", "github-alexp-oscars", "local"),
        default="auto",
    )
    p.add_argument("--kaggle-slug", default=DEFAULT_KAGGLE_SLUG)
    p.add_argument("--input", type=Path, help="Local CSV when --source local.")
    p.add_argument("--input-label", default="local-csv")
    p.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    p.add_argument("--csv-out", type=Path, default=DEFAULT_CSV)
    p.add_argument("--write-index", action="store_true", help="Write a24_script_slug_index.json")
    p.add_argument("--skip-index", action="store_true")
    return p.parse_args()


def resolve_rows(args: argparse.Namespace) -> tuple[list[dict], str]:
    if args.source == "local":
        if not args.input or not args.input.exists():
            raise SystemExit("--source local requires --input")
        return rows_from_local_csv(args.input, args.input_label), args.input_label

    if args.source in ("github-alexp", "github-alexp-oscars"):
        url = ALEXPMORTON_RELEASED_CSV if args.source == "github-alexp" else ALEXPMORTON_OSCARS_CSV
        return rows_from_alexp_morton(url), "AlexPMorton/A24-Movies-EDA"

    if args.source == "kaggle" or args.source == "auto":
        slug = args.kaggle_slug
        fname = KAGGLE_METADATA_SLUGS.get(slug, "a24_data_cleaned.csv")
        cache = ROOT / "data" / "ingest" / ".cache" / "kaggle"
        path = download_kaggle_file(slug, fname, cache)
        if path:
            return rows_from_local_csv(path, f"kaggle/{slug}"), f"kaggle/{slug}"
        if args.source == "kaggle":
            raise SystemExit(
                "Kaggle download failed. Install CLI (`pip install kaggle`), set "
                "~/.kaggle/kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY, then:\n"
                f"  kaggle datasets download -d {slug} -f {fname}\n"
                f"  python3 scripts/scrape_a24_metadata.py --source local --input {fname}"
            )

    return rows_from_alexp_morton(ALEXPMORTON_RELEASED_CSV), "AlexPMorton/A24-Movies-EDA"


def main() -> None:
    args = parse_args()
    rows, provenance = resolve_rows(args)
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "provenance": provenance,
        "count": len(rows),
        "titles": rows,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_titles_csv(rows, args.csv_out)
    print(f"Wrote {args.json_out} ({len(rows)} titles, source={provenance})")
    print(f"Wrote {args.csv_out}")

    if args.write_index or not args.skip_index:
        index = build_script_slug_index(rows)
        INDEX_JSON.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {INDEX_JSON} (guessed Script Slug URLs only; no HTTP scrape)")


if __name__ == "__main__":
    main()