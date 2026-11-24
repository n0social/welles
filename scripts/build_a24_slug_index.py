"""Build or refresh A24 Script Slug URL metadata (titles + detail URLs only).

Legal / product stance
----------------------
Script Slug Legal ToS §9 forbids automated scraping and systematic download
without written permission. **This repo does not perform live studio listing
scrapes by default.**

The public `/scripts/studio/a24` page loads script cards client-side; a single
HTML fetch does not reliably expose title→URL pairs. Default mode therefore:

* Reuses / extends `data/ingest/a24_script_slug_index.json` from local
  `a24_titles` metadata (same approach as `scrape_a24_metadata.py`).
* Optionally syncs those URLs into `data/ingest/a24_download_queue.json`
  for the user-operated `download_screenplay_pdf.py` bot.

Optional `--fetch-listing-html` saves **one** listing HTML snapshot under
`data/ingest/.cache/` for manual inspection (no PDFs, no pagination loop).

No PDF download happens in this script — use `download_screenplay_pdf.py`.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from a24_metadata_lib import script_slug_guess_path, slug_title  # noqa: E402

INDEX_PATH = ROOT / "data" / "ingest" / "a24_script_slug_index.json"
TITLES_PATH = ROOT / "data" / "ingest" / "a24_titles.json"
QUEUE_PATH = ROOT / "data" / "ingest" / "a24_download_queue.json"
CACHE_DIR = ROOT / "data" / "ingest" / ".cache"
STUDIO_LISTING = "https://www.scriptslug.com/scripts/studio/a24"
USER_AGENT = (
    "WellesScreenplayFetch/1.0 (+local; metadata-only; personal-study)"
)


def utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_titles(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("titles") or data.get("entries") or []


def build_entries_from_titles(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        title = (row.get("title") or row.get("name") or "").strip()
        year = str(row.get("release_year") or row.get("year") or "").strip()
        if not title:
            continue
        path_guess = row.get("script_slug_path_guess") or script_slug_guess_path(title, year)
        slug_url = (
            f"https://www.scriptslug.com{path_guess}" if path_guess else None
        )
        out.append(
            {
                "title": title,
                "release_year": year,
                "title_slug": slug_title(title),
                "script_slug_url": slug_url,
                "script_slug_url_verified": False,
                "note": "Guessed path for manual browser check or user-operated download.",
            }
        )
    return out


def build_index_doc(entries: list[dict]) -> dict:
    return {
        "survey_date": utc_date(),
        "automated_scrape_performed": False,
        "live_listing_scrape": False,
        "script_slug_policy": {
            "studio_listing": STUDIO_LISTING,
            "url_pattern_note": "https://www.scriptslug.com/script/{kebab-title}-{year}",
            "robots_txt": "https://www.scriptslug.com/robots.txt",
            "ai_policy": "https://www.scriptslug.com/ai.txt",
            "terms": "https://www.scriptslug.com/legal",
            "reason_no_live_scrape": (
                "ToS §9 + client-rendered studio listing; default uses local title metadata only."
            ),
        },
        "cole_haddon": {
            "post_url": "https://colehaddon.substack.com/p/60-a24-screenplays-to-download-and",
            "format": "paid_substack_pdf_links",
            "automated_scrape": False,
            "reason": "Paid Substack; user must fetch PDF links manually.",
        },
        "entries": entries,
    }


def sync_queue_from_index(index: dict, queue_path: Path) -> dict:
    items = []
    for ent in index.get("entries") or []:
        page = ent.get("script_slug_url") or ""
        if not page:
            continue
        slug = page.rstrip("/").split("/")[-1]
        items.append(
            {
                "id": slug,
                "title": ent.get("title"),
                "release_year": ent.get("release_year"),
                "page_url": page,
                "pdf_url": None,
                "out_name": f"{slug}.pdf",
                "source": "script_slug",
                "status": "pending",
            }
        )
    doc = {
        "version": 1,
        "updated": utc_date(),
        "legal_note": (
            "User-operated queue for download_screenplay_pdf.py. "
            "Personal/education only; never commit resulting PDFs."
        ),
        "items": items,
    }
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return doc


def fetch_listing_html_snapshot(dest: Path) -> None:
    req = urllib.request.Request(
        STUDIO_LISTING,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        data = resp.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="A24 Script Slug index (stubbed live scrape by default).")
    p.add_argument("--titles", type=Path, default=TITLES_PATH)
    p.add_argument("--index-out", type=Path, default=INDEX_PATH)
    p.add_argument("--sync-queue", action="store_true", help="Write a24_download_queue.json from index")
    p.add_argument("--queue-out", type=Path, default=QUEUE_PATH)
    p.add_argument(
        "--fetch-listing-html",
        action="store_true",
        help="Save one studio listing HTML snapshot to .cache (no parse; SPA listing).",
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_titles(args.titles)
    if not rows:
        print(
            f"No titles in {args.titles}. Run: python3 scripts/scrape_a24_metadata.py",
            file=sys.stderr,
        )
        sys.exit(1)

    entries = build_entries_from_titles(rows)
    doc = build_index_doc(entries)

    if args.fetch_listing_html:
        snap = CACHE_DIR / f"scriptslug_a24_listing_{utc_date()}.html"
        if args.dry_run:
            print(f"[dry-run] would save listing HTML → {snap}")
        else:
            fetch_listing_html_snapshot(snap)
            doc["listing_html_snapshot"] = str(snap.relative_to(ROOT))
            print(f"Saved listing HTML snapshot (SPA; parse manually if needed): {snap}")

    if args.dry_run:
        print(f"[dry-run] would write {len(entries)} entries → {args.index_out}")
    else:
        args.index_out.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"Wrote {args.index_out} ({len(entries)} entries, live_listing_scrape=false)")

    if args.sync_queue:
        if args.dry_run:
            print(f"[dry-run] would sync queue → {args.queue_out}")
        else:
            q = sync_queue_from_index(doc, args.queue_out)
            print(f"Wrote {args.queue_out} ({len(q['items'])} pending template items)")


if __name__ == "__main__":
    main()