"""User-operated, one-at-a-time screenplay PDF fetcher (local cache only).

Legal / product stance
----------------------
* Script Slug PDFs: personal / educational fair use on **your machine** only.
  No commercial redistribution. Honor takedowns. This bot does **not** grant
  ML-training rights (see scriptslug.com/ai.txt and ToS §9).
* Cole Haddon / Substack links: you must have subscriber access; one-off downloads.
* **Never commit PDF bodies** to git (`data/scripts/a24/incoming/*.pdf` is gitignored).
* Default: no full-site crawl — only URLs you pass on the CLI or approve in
  `data/ingest/a24_download_queue.json`, or detail URLs already listed in
  `data/ingest/a24_script_slug_index.json` when you build a queue from that file.

The repo maintainers provide this helper; **you** run it and accept site terms.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "scripts" / "a24" / "incoming"
DEFAULT_QUEUE = ROOT / "data" / "ingest" / "a24_download_queue.json"
DEFAULT_LOG = ROOT / "data" / "ingest" / "download_log.jsonl"
EXTRACT_SCRIPT = Path(__file__).resolve().parent / "extract_screenplay_pdf.py"

USER_AGENT = (
    "WellesScreenplayFetch/1.0 (+https://github.com/n0social/welles; "
    "user-operated; personal-study; one-request-at-a-time)"
)
TIMEOUT_SEC = 120
PDF_MAGIC = b"%PDF"

SCRIPT_SLUG_PAGE = re.compile(
    r"https?://(?:www\.)?scriptslug\.com/script/[\w%-]+", re.I
)
SCRIPT_SLUG_PDF = re.compile(
    r"https://assets\.scriptslug\.com/live/pdf/scripts/[\w.-]+\.pdf(?:\?[^\"'\s<>]*)?",
    re.I,
)
DATA_PDF_URL = re.compile(r'data-pdf-url="([^"]+\.pdf[^"]*)"', re.I)
ENCODING_CONTENT_URL = re.compile(
    r'"contentUrl"\s*:\s*"(https://assets\.scriptslug\.com/[^"]+\.pdf[^"]*)"',
    re.I,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def http_get(
    url: str,
    *,
    accept: str | None = None,
    max_bytes: int | None = None,
) -> tuple[bytes, str | None]:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC, context=ctx) as resp:
        ctype = resp.headers.get("Content-Type")
        data = resp.read(max_bytes) if max_bytes else resp.read()
        return data, ctype


def resolve_pdf_url(url: str) -> str:
    url = url.strip()
    lower = url.lower()
    if lower.endswith(".pdf") or "assets.scriptslug.com/live/pdf/" in lower:
        return url
    if SCRIPT_SLUG_PAGE.search(url):
        html_bytes, _ = http_get(url, accept="text/html")
        html = html_bytes.decode("utf-8", errors="replace")
        for pattern in (DATA_PDF_URL, ENCODING_CONTENT_URL, SCRIPT_SLUG_PDF):
            m = pattern.search(html)
            if m:
                return m.group(1) if m.lastindex else m.group(0)
        raise ValueError(f"No PDF URL found on Script Slug page: {url}")
    raise ValueError(
        "URL must be a direct .pdf link or a scriptslug.com/script/... page "
        "(approve each URL yourself; no site-wide crawl)."
    )


def safe_filename(name: str, fallback: str) -> str:
    base = name.strip() if name else fallback
    if not base.lower().endswith(".pdf"):
        base += ".pdf"
    base = re.sub(r"[^\w.\-]+", "_", base).strip("._")
    return base or "screenplay.pdf"


def stem_from_url(url: str) -> str:
    path = urllib.request.urlparse(url).path
    name = Path(path).name
    if name.lower().endswith(".pdf"):
        return name
    part = path.rstrip("/").split("/")[-1]
    return f"{part}.pdf"


def download_pdf(pdf_url: str, dest: Path) -> dict[str, Any]:
    if dest.exists() and dest.stat().st_size > 0:
        return {
            "status": "skipped_exists",
            "path": str(dest),
            "bytes": dest.stat().st_size,
            "pdf_url": pdf_url,
        }
    data, ctype = http_get(pdf_url)
    if not data.startswith(PDF_MAGIC):
        raise ValueError(
            f"Response from {pdf_url} does not look like a PDF "
            f"(Content-Type: {ctype!r}, {len(data)} bytes)."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {
        "status": "downloaded",
        "path": str(dest),
        "bytes": len(data),
        "pdf_url": pdf_url,
        "content_type": ctype,
    }


def load_queue(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_queue(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pending_items(doc: dict[str, Any]) -> list[dict[str, Any]]:
    items = doc.get("items") or []
    return [it for it in items if (it.get("status") or "pending") == "pending"]


def process_item(
    item: dict[str, Any],
    out_dir: Path,
    log_path: Path,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    page_url = (item.get("page_url") or item.get("url") or "").strip()
    pdf_url = (item.get("pdf_url") or "").strip() or None
    source_url = pdf_url or page_url
    if not source_url:
        raise ValueError("Queue item needs page_url or pdf_url")

    title = item.get("title") or item.get("id") or "screenplay"
    out_name = item.get("out_name") or stem_from_url(pdf_url or page_url)
    dest = out_dir / safe_filename(out_name, stem_from_url(source_url))

    record: dict[str, Any] = {
        "ts": utc_now(),
        "title": title,
        "page_url": page_url or None,
        "source_url": source_url,
        "dest": str(dest),
        "dry_run": dry_run,
    }

    if dry_run:
        record["status"] = "dry_run"
        log_event(log_path, record)
        print(f"[dry-run] would fetch {source_url} → {dest}")
        return record

    try:
        resolved = pdf_url or resolve_pdf_url(page_url)
        record["pdf_url"] = resolved
        result = download_pdf(resolved, dest)
        record.update(result)
        item["status"] = "done" if result["status"] == "downloaded" else "skipped_exists"
        item["last_pdf_url"] = resolved
        item["local_path"] = str(dest)
        item["updated_at"] = utc_now()
        print(f"{result['status']}: {dest} ({result['bytes']:,} bytes)")
    except (urllib.error.URLError, ValueError, OSError) as exc:
        record["status"] = "error"
        record["error"] = str(exc)
        item["status"] = "error"
        item["last_error"] = str(exc)
        item["updated_at"] = utc_now()
        print(f"error: {title}: {exc}")

    log_event(log_path, record)
    return record


def suggest_extract(dest: Path) -> None:
    if EXTRACT_SCRIPT.is_file() and dest.exists():
        print(
            f"Next: python3 {EXTRACT_SCRIPT.relative_to(ROOT)} "
            f"(PDF at {dest.relative_to(ROOT)})"
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="User-operated one-by-one screenplay PDF download (local cache)."
    )
    p.add_argument("--url", help="Direct PDF or Script Slug script page URL")
    p.add_argument("--out-name", help="Filename under --out-dir (default: from URL)")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    p.add_argument("--from-queue", action="store_true", help="Process queue item(s)")
    p.add_argument(
        "--max-per-run",
        type=int,
        default=1,
        help="Max pending queue items per invocation (default: 1)",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Seconds to sleep between queue items in one run (e.g. 30)",
    )
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--i-accept-personal-use-only",
        action="store_true",
        help="Required acknowledgment: personal/education use; no redistribution.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not args.i_accept_personal_use_only:
        raise SystemExit(
            "Pass --i-accept-personal-use-only to confirm personal/education use, "
            "no commercial redistribution, and honoring takedowns "
            "(see script docstring and data/ingest/script_sources.md)."
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.url:
        item = {
            "title": args.out_name or args.url,
            "page_url": args.url,
            "out_name": args.out_name,
        }
        record = process_item(item, args.out_dir, args.log, dry_run=args.dry_run)
        if not args.dry_run and record.get("status") in ("downloaded", "skipped_exists"):
            suggest_extract(Path(record["dest"]))
        return

    if not args.from_queue:
        raise SystemExit("Provide --url or --from-queue (see --help).")

    doc = load_queue(args.queue)
    pend = pending_items(doc)
    if not pend:
        print(f"No pending items in {args.queue}")
        return

    n = min(max(args.max_per_run, 1), len(pend))
    for i, item in enumerate(pend[:n]):
        if i > 0 and args.delay > 0:
            time.sleep(args.delay)
        process_item(item, args.out_dir, args.log, dry_run=args.dry_run)

    if not args.dry_run:
        save_queue(args.queue, doc)
        last_dest = pend[0].get("local_path")
        if last_dest:
            suggest_extract(Path(last_dest))


if __name__ == "__main__":
    main()