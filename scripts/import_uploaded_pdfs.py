"""Verify user-uploaded screenplay PDFs in incoming/, then batch-extract staging .txt.

Does not download from the web — use manual browser save or download_screenplay_pdf.py first.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO_DIRS = {
    "a24": (
        ROOT / "data" / "scripts" / "a24" / "incoming",
        ROOT / "data" / "scripts" / "a24",
    ),
    "welles": (
        ROOT / "data" / "scripts" / "welles" / "incoming",
        ROOT / "data" / "scripts" / "welles",
    ),
}
EXTRACT = Path(__file__).resolve().parent / "extract_screenplay_pdf.py"

NAME_PATTERN = re.compile(r"^.+_\d{4}\.pdf$", re.IGNORECASE)
KEBAB_YEAR_PATTERN = re.compile(r"^.+-\d{4}\.pdf$", re.IGNORECASE)
PDF_MAGIC = b"%PDF"

# Legacy upload path (GitHub UI drop at repo root)
LEGACY_A24_PDF_DIR = ROOT / "scripts"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Check incoming/*.pdf naming, then batch-extract staging .txt files."
    )
    p.add_argument(
        "--studio",
        choices=sorted(STUDIO_DIRS),
        default="a24",
        help="Which incoming/ + excerpt output dir (default: a24).",
    )
    p.add_argument(
        "--incoming",
        type=Path,
        default=None,
        help="Override incoming folder (default: data/scripts/<studio>/incoming/).",
    )
    p.add_argument("--strict-naming", action="store_true", help="Exit 1 if any PDF breaks Title_Year.pdf.")
    p.add_argument("--dry-run", action="store_true", help="Verify only; do not run extract.")
    return p.parse_args()


def verify_pdf(path: Path) -> list[str]:
    issues: list[str] = []
    if not (NAME_PATTERN.match(path.name) or KEBAB_YEAR_PATTERN.match(path.name)):
        issues.append(f"naming: expected Title_Year.pdf or title-YYYY.pdf, got {path.name}")
    try:
        head = path.read_bytes()[:5]
    except OSError as exc:
        issues.append(f"read: {exc}")
        return issues
    if head != PDF_MAGIC:
        issues.append("not a PDF (missing %PDF header)")
    return issues


def main() -> None:
    args = parse_args()
    incoming_default, out_dir = STUDIO_DIRS[args.studio]
    args.incoming = args.incoming or incoming_default
    args.incoming.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(args.incoming.glob("*.pdf"))
    if not pdfs and args.studio == "a24" and LEGACY_A24_PDF_DIR.is_dir():
        legacy = sorted(LEGACY_A24_PDF_DIR.glob("*.pdf"))
        if legacy:
            print(
                f"Found {len(legacy)} PDF(s) in {LEGACY_A24_PDF_DIR} — "
                f"moving into {args.incoming} …"
            )
            for src in legacy:
                dest = args.incoming / src.name
                if dest.exists():
                    print(f"  skip (exists): {dest.name}")
                    continue
                src.rename(dest)
                print(f"  moved {src.name}")
            pdfs = sorted(args.incoming.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in {args.incoming}")
        print("Upload files named Title_Year.pdf (e.g. Moonlight_2016.pdf), then re-run.")
        raise SystemExit(1)

    bad = False
    for pdf in pdfs:
        issues = verify_pdf(pdf)
        if issues:
            bad = True
            print(f"{pdf.name}:")
            for msg in issues:
                print(f"  - {msg}")
        else:
            size_kb = pdf.stat().st_size // 1024
            print(f"OK  {pdf.name} ({size_kb} KiB)")

    if bad and args.strict_naming:
        raise SystemExit(1)

    if args.dry_run:
        print("\nDry run — skipped extract.")
        print(f"Next: python3 scripts/ingest_scripts.py --dataset manual --filter {args.studio}")
        return

    cmd = [
        sys.executable,
        str(EXTRACT),
        "--incoming",
        str(args.incoming),
        "--out-dir",
        str(out_dir),
    ]
    print("\nRunning extract_screenplay_pdf.py …")
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    print(
        f"\nExcerpts → {out_dir}/*_excerpt.txt\n"
        "Next:\n"
        f"  python3 scripts/ingest_scripts.py --dataset manual --filter {args.studio}"
    )


if __name__ == "__main__":
    main()