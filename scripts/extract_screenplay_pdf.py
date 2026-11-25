"""Convert user-dropped screenplay PDFs to .txt (local incoming/ only).

Modes:
  staging (default): short action-only excerpts for STAGE/WRITE transforms.
  full: entire script as {_stem}_full.txt, scene-chunked {_stem}_scenes/ optional via ingest.

Does not download from Script Slug, Cole Haddon, or the web.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "data" / "scripts" / "a24" / "incoming"
OUT_DIR = ROOT / "data" / "scripts" / "a24"

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ingest_scripts import chunk_manual_text, chunk_screenplay_full, strip_dialogue_plain, word_count  # noqa: E402


def pdf_to_text(path: Path) -> str:
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "Need `pdftotext` (poppler) on PATH or `pip install pypdf` for PDF extraction."
        ) from exc
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def stem_from_pdf(path: Path) -> str:
    return re.sub(r"[^\w.-]+", "_", path.stem.lower()).strip("_")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PDF → .txt for manual screenplay drops.")
    p.add_argument("--incoming", type=Path, default=INCOMING)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument(
        "--mode",
        choices=("staging", "full"),
        default="staging",
        help="full: write Title_full.txt with entire screenplay text (dialogue kept).",
    )
    p.add_argument("--min-words", type=int, default=25)
    p.add_argument("--max-words", type=int, default=150)
    p.add_argument("--max-chunks", type=int, default=3, help="Staging: cap excerpt chunks per PDF.")
    p.add_argument(
        "--full-max-words",
        type=int,
        default=380,
        help="Full mode: max words per scene chunk (fit ~1024–2048 train length).",
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "full":
        args.min_words = max(args.min_words, 60)
        args.max_words = args.full_max_words

    args.incoming.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(args.incoming.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in {args.incoming} (drop files there manually).")
        return

    for pdf in pdfs:
        raw = pdf_to_text(pdf)
        stem = stem_from_pdf(pdf)

        if args.mode == "full":
            full_path = args.out_dir / f"{stem}_full.txt"
            header = (
                f"# Full screenplay text from {pdf.name} (for training; not for redistribution)\n\n"
            )
            if args.dry_run:
                print(f"Would write {full_path} ({word_count(raw)} words)")
                scenes = chunk_screenplay_full(
                    raw, args.min_words, args.max_words, keep_dialogue=True
                )
                print(f"  → {len(scenes)} scene chunks")
                continue
            full_path.write_text(header + raw, encoding="utf-8")
            scenes = chunk_screenplay_full(raw, args.min_words, args.max_words, keep_dialogue=True)
            print(f"Wrote {full_path} ({word_count(raw)} words, {len(scenes)} scenes)")
            continue

        staging = strip_dialogue_plain(raw)
        chunks = chunk_manual_text(staging, args.min_words, args.max_words)[: args.max_chunks]
        if not chunks:
            print(f"Skip {pdf.name}: insufficient staging text after dialogue strip.")
            continue
        out_name = f"{stem}_excerpt.txt"
        out_path = args.out_dir / out_name
        body = "\n\n---\n\n".join(chunks)
        header = (
            f"# Staging excerpts from {pdf.name} (auto-generated; not for redistribution)\n\n"
        )
        if args.dry_run:
            print(f"Would write {out_path} ({word_count(body)} words from {len(chunks)} chunks)")
            continue
        out_path.write_text(header + body, encoding="utf-8")
        print(f"Wrote {out_path} ({len(chunks)} chunks)")


if __name__ == "__main__":
    main()