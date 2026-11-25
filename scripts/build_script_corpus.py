"""Phase 1: extract all uploaded PDFs and build a local script SFT corpus (then train separately).

Outputs (gitignored by default):
  data/scripts/{welles,a24}/*_full.txt
  data/ingest/script_pairs.jsonl
Optional:
  data/ingest/train_scripts_only.jsonl  (messages format via prepare_data)

Does not download from the web.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PAIRS = ROOT / "data" / "ingest" / "script_pairs.jsonl"
IMPORT = ROOT / "scripts" / "import_uploaded_pdfs.py"
INGEST = ROOT / "scripts" / "ingest_scripts.py"
PREPARE = ROOT / "scripts" / "prepare_data.py"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def file_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build full-script corpus from uploaded PDFs.")
    p.add_argument("--studios", default="welles,a24", help="Comma: welles, a24")
    p.add_argument(
        "--task-mix",
        default="verbatim,continue,compose,bridge,structure",
        help="Passed to ingest_scripts.py",
    )
    p.add_argument("--skip-extract", action="store_true", help="Only re-run ingest on existing *_full.txt")
    p.add_argument(
        "--build-train",
        action="store_true",
        help="Also run prepare_data.py → data/train.jsonl (scripts-heavy mix).",
    )
    p.add_argument("--boost-kane", type=int, default=3)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    py = sys.executable

    if not args.skip_extract:
        for studio in [s.strip() for s in args.studios.split(",") if s.strip()]:
            print(f"\n--- extract studio: {studio} ---")
            proc = subprocess.run(
                [py, str(IMPORT), "--studio", studio, "--full-screenplay"],
                cwd=ROOT,
            )
            if proc.returncode != 0:
                print(
                    f"WARN: import {studio} exited {proc.returncode} "
                    "(often Git LFS — run git lfs pull). Continuing ingest for existing *_full.txt …"
                )

    run(
        [
            py,
            str(INGEST),
            "--dataset",
            "manual",
            "--filter",
            "all",
            "--screenplay-mode",
            "full",
            "--max-pairs",
            "0",
            "--task-mix",
            args.task_mix,
            "--boost-titles",
            "citizen kane",
            "--boost-repeat",
            str(args.boost_kane),
            "-o",
            str(SCRIPT_PAIRS),
        ]
    )

    lines = count_jsonl_lines(SCRIPT_PAIRS)
    mb = file_size_mb(SCRIPT_PAIRS)
    print(f"\nCorpus: {SCRIPT_PAIRS}")
    print(f"  Rows: {lines}")
    print(f"  Size: {mb:.2f} MiB")

  # Phase 2 training (separate step):
    print("\nPhase 2 — train off the corpus:")
    print(f"  python3 {PREPARE.name} --fetch-scripts --script-dataset manual --script-filter all \\")
    print("    --script-screenplay-mode full --max-script-ingest 0 --max-scripts 0 \\")
    print(f"    --scripts-cache {SCRIPT_PAIRS} --gold-repeat 3 --max-cinema 40")
    print(f"  python3 scripts/train.py  # reads data/train.jsonl")

    if args.build_train:
        run(
            [
                py,
                str(PREPARE),
                "--scripts-cache",
                str(SCRIPT_PAIRS),
                "--fetch-scripts",
                "--script-dataset",
                "manual",
                "--script-filter",
                "all",
                "--script-screenplay-mode",
                "full",
                "--max-script-ingest",
                "0",
                "--max-scripts",
                "0",
                "--gold-repeat",
                "3",
                "--max-cinema",
                "40",
                "--max-examples",
                "80",
            ]
        )
        print(f"Wrote data/train.jsonl ({file_size_mb(ROOT / 'data/train.jsonl'):.2f} MiB)")


if __name__ == "__main__":
    main()