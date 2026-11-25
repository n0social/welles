"""Download third-party screenplay datasets into data/external/ (local / Colab; not committed at full size).

Sources:
  - Inkwell-Software/screenplay-revision-evaluation (HF, CC0-1.0)
  - Atum09/screenplay-dataset (HF; check LICENSE on Hub)
  - gufukuro/movie-scripts-corpus (Kaggle, CC BY-NC-SA 4.0; requires Kaggle API)

Usage:
  python3 scripts/fetch_external_datasets.py --all
  python3 scripts/fetch_external_datasets.py --hf inkwell,atum09
  python3 scripts/fetch_external_datasets.py --kaggle-movie-corpus
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile

import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
LOG = ROOT / "data" / "ingest" / "download_log.jsonl"

INKWELL_REPO = "Inkwell-Software/screenplay-revision-evaluation"
ATUM09_REPO = "Atum09/screenplay-dataset"
KAGGLE_SLUG = "gufukuro/movie-scripts-corpus"
DATAVERSE_FILE_ID = 10187426
DATAVERSE_URL = f"https://dataverse.harvard.edu/api/access/datafile/{DATAVERSE_FILE_ID}"


def log_event(event: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {**event, "ts": datetime.now(timezone.utc).isoformat()}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def fetch_hf(repo_id: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {repo_id} -> {dest}")
    path = snapshot_download(
        repo_id=repo_id,
        repo_type="dataset",
        local_dir=str(dest),
        local_dir_use_symlinks=False,
    )
    log_event({"source": repo_id, "kind": "huggingface", "path": path, "status": "ok"})
    print(f"Done: {path}")


def fetch_dataverse_movie_corpus(dest: Path) -> None:
    """Harvard Dataverse mirror of gufukuro/kaggle Movie Scripts Corpus (~660 MB zip)."""
    dest.mkdir(parents=True, exist_ok=True)
    zip_path = dest / "MovieScriptsCorpus.zip"
    if zip_path.exists() and zip_path.stat().st_size > 100_000_000:
        print(f"Already present: {zip_path}")
    else:
        print(f"Downloading {DATAVERSE_URL} -> {zip_path}")
        req = urllib.request.Request(
            DATAVERSE_URL,
            headers={"User-Agent": "welles-fetch/1.0 (dataset mirroring)"},
        )
        with urllib.request.urlopen(req, timeout=3600) as resp:
            with zip_path.open("wb") as out:
                shutil.copyfileobj(resp, out, length=16 * 1024 * 1024)
    extract_marker = dest / ".extracted"
    if not extract_marker.exists():
        print(f"Extracting {zip_path} -> {dest}")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest)
        extract_marker.write_text("ok\n", encoding="utf-8")
    log_event(
        {
            "source": "doi:10.7910/DVN/PZTL2L",
            "kind": "dataverse",
            "path": str(dest),
            "status": "ok",
        }
    )


def fetch_kaggle_movie_corpus(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    kaggle = shutil.which("kaggle")
    if not kaggle:
        raise SystemExit(
            "Kaggle CLI not installed. Try: pip install kaggle\n"
            "Then place kaggle.json in ~/.kaggle/ (API token from Kaggle account settings)."
        )
    cmd = [
        kaggle,
        "datasets",
        "download",
        "-d",
        KAGGLE_SLUG,
        "-p",
        str(dest),
        "--unzip",
    ]
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        log_event(
            {
                "source": KAGGLE_SLUG,
                "kind": "kaggle",
                "path": str(dest),
                "status": "error",
                "code": proc.returncode,
            }
        )
        raise SystemExit(proc.returncode)
    log_event({"source": KAGGLE_SLUG, "kind": "kaggle", "path": str(dest), "status": "ok"})


def write_manifest() -> None:
    manifest_path = EXTERNAL / "MANIFEST.json"
    entries = []
    for name in ["inkwell-screenplay-revision-evaluation", "atum09-screenplay-dataset", "kaggle-movie-scripts-corpus"]:
        p = EXTERNAL / name
        if not p.exists():
            continue
        size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        entries.append({"dir": name, "bytes": size, "files": sum(1 for _ in p.rglob("*") if _.is_file())})
    manifest_path.write_text(json.dumps({"updated": datetime.now(timezone.utc).isoformat(), "entries": entries}, indent=2))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch external screenplay datasets.")
    p.add_argument("--all", action="store_true", help="HF datasets + Kaggle corpus")
    p.add_argument(
        "--hf",
        default="",
        help="Comma: inkwell,atum09",
    )
    p.add_argument("--kaggle-movie-corpus", action="store_true")
    p.add_argument(
        "--dataverse-movie-corpus",
        action="store_true",
        help="Harvard Dataverse zip (same corpus as Kaggle; no API token)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    hf = set()
    if args.all:
        hf.update({"inkwell", "atum09"})
        args.dataverse_movie_corpus = True
    if args.hf:
        hf.update(x.strip().lower() for x in args.hf.split(",") if x.strip())

    if not hf and not args.kaggle_movie_corpus and not args.dataverse_movie_corpus:
        print(
            "Nothing selected. Use --all, --hf inkwell,atum09, "
            "--kaggle-movie-corpus, or --dataverse-movie-corpus."
        )
        raise SystemExit(1)

    EXTERNAL.mkdir(parents=True, exist_ok=True)

    if "inkwell" in hf:
        fetch_hf(INKWELL_REPO, EXTERNAL / "inkwell-screenplay-revision-evaluation")
    if "atum09" in hf:
        fetch_hf(ATUM09_REPO, EXTERNAL / "atum09-screenplay-dataset")
    if args.kaggle_movie_corpus:
        fetch_kaggle_movie_corpus(EXTERNAL / "kaggle-movie-scripts-corpus")
    if args.dataverse_movie_corpus:
        fetch_dataverse_movie_corpus(EXTERNAL / "kaggle-movie-scripts-corpus")

    write_manifest()
    print(f"Manifest: {EXTERNAL / 'MANIFEST.json'}")


if __name__ == "__main__":
    main()