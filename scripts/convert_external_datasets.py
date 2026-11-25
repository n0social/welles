"""Export small Welles-friendly samples from data/external/ (optional ingest inputs)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
OUT = ROOT / "data" / "ingest" / "external_samples"

INKWELL = EXTERNAL / "inkwell-screenplay-revision-evaluation" / "data" / "cases.jsonl"
ATUM09_TRAIN = EXTERNAL / "atum09-screenplay-dataset" / "data" / "train"


def export_inkwell_eval(max_rows: int = 48) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "inkwell_revision_eval.jsonl"
    if not INKWELL.exists():
        raise SystemExit(f"Missing {INKWELL}. Run fetch_external_datasets.py --hf inkwell")
    lines = INKWELL.read_text(encoding="utf-8").splitlines()
    with dest.open("w", encoding="utf-8") as out:
        for line in lines[:max_rows]:
            if line.strip():
                out.write(line + "\n")
    return dest


def export_atum09_filtered(categories: str, max_rows: int) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    want = {c.strip() for c in categories.split(",") if c.strip()}
    dest = OUT / f"atum09_{'-'.join(sorted(want))}_sample.jsonl"
    if not ATUM09_TRAIN.exists():
        raise SystemExit(f"Missing {ATUM09_TRAIN}. Run fetch_external_datasets.py --hf atum09")
    n = 0
    with dest.open("w", encoding="utf-8") as out:
        for path in sorted(ATUM09_TRAIN.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                cat = row.get("category") or ""
                if want and cat not in want:
                    continue
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
                if n >= max_rows:
                    break
            if n >= max_rows:
                break
    return dest


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--inkwell-eval", action="store_true")
    p.add_argument(
        "--atum09-categories",
        default="script_coverage,rewrite_punchup",
        help="Comma categories to sample",
    )
    p.add_argument("--atum09-max", type=int, default=500)
    args = p.parse_args()
    did = False
    if args.inkwell_eval:
        path = export_inkwell_eval()
        print(f"Wrote {path}")
        did = True
    if args.atum09_max > 0:
        path = export_atum09_filtered(args.atum09_categories, args.atum09_max)
        print(f"Wrote {path}")
        did = True
    if not did:
        raise SystemExit("Pass --inkwell-eval and/or set --atum09-max > 0")


if __name__ == "__main__":
    main()