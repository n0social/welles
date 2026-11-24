"""Ingest screenplay staging text for Welles SFT — HF caps + manual drop dirs.

Default: MovieSum XML stage directions / scene descriptions only (no dialogue).
See data/ingest/script_sources.md for filmography, A24 findings, and legal warnings.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "ingest" / "script_pairs.jsonl"
WELLES_DIR = ROOT / "data" / "scripts" / "welles"
A24_DIR = ROOT / "data" / "scripts" / "a24"

MOVIESUM_DS = "rohitsaxena/MovieSum"
MOVIES_DS = "IsmaelMousa/movies"

# MovieSum `movie_name` patterns (title before _YEAR). Not exhaustive — boosts recall.
WELLES_MOVIESUM_KEYS = (
    "citizen kane",
    "magnificent ambersons",
    "the stranger_1946",
    "stranger_1946",
    "lady from shanghai",
    "macbeth_1948",
    "macbeth_195",
    "othello_19",
    "touch of evil",
    "the trial_1962",
    "trial_1962",
    "chimes at midnight",
    "f for fake",
    "journey into fear",
    "immortal story",
    "mr. arkadin",
    "confidential report",
    "other side of the wind",
    "too much johnson",
    "filming othello",
)

# Prefer `Title_YYYY` MovieSum keys to avoid substring false positives (e.g. "men" in Phantom Menace).
A24_MOVIESUM_KEYS = (
    "moonlight_2016",
    "lady bird_2017",
    "hereditary_2018",
    "midsommar_2019",
    "eighth grade_2018",
    "the witch_2015",
    "ex machina_2015",
    "room_2015",
    "the lobster_2015",
    "swiss army man_2016",
    "everything everywhere all at once_2022",
    "uncut gems_2019",
    "the green knight_2021",
    "minari_2020",
    "last night in soho_2021",
    "the farewell_2019",
    "first cow_2019",
    "the lighthouse_2019",
    "good time_2017",
    "saint maud_2019",
    "men_2022",
    "pearl_2022",
    "x_2022",
    "bones and all_2022",
    "aftersun_2022",
    "the whale_2022",
    "beau is afraid_2023",
    "past lives_2023",
    "priscilla_2023",
    "dream scenario_2023",
)

WRITE = "WRITE. New prose in Welles's voice.\n\n"

# Reuse cinema filters / MovieSum XML parsing
_SCRIPTS = Path(__file__).resolve().parent
import sys

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ingest_cinema import (  # noqa: E402
    clamp_words,
    extract_script_excerpts,
    has_cjk,
    load_pairs,
    looks_hype,
    passes_filters,
    row_pair,
    script_excerpt_prompt,
    word_count,
)

DATASETS = ("moviesum", "movies", "manual")


def _norm_title(name: str) -> str:
    return re.sub(r"\s+", "_", name.strip().lower())


def matches_filter(movie_name: str, filt: str) -> bool:
    name = _norm_title(movie_name)
    if filt == "all":
        return True
    keys = WELLES_MOVIESUM_KEYS if filt == "welles" else A24_MOVIESUM_KEYS
    for key in keys:
        k = _norm_title(key)
        if name == k:
            return True
        if "_" in k:
            title_part, _, year = k.rpartition("_")
            if year.isdigit() and name.startswith(f"{title_part}_{year}"):
                return True
            if name.startswith(f"{title_part}_"):
                return True
        elif k in name:
            return True
    return False


def pairs_from_moviesum(
    filt: str,
    max_pairs: int,
    scripts_cap: int,
    min_words: int,
    max_words: int,
    max_per_script: int,
) -> list[dict]:
    ds = load_dataset(MOVIESUM_DS, split="train", streaming=True)
    pairs: list[dict] = []
    scanned = 0
    for ex in ds:
        if len(pairs) >= max_pairs:
            break
        name = (ex.get("movie_name") or "Unknown").strip()
        if filt != "all" and not matches_filter(name, filt):
            continue
        scanned += 1
        if scanned > scripts_cap:
            break
        script = ex.get("script") or ""
        if not script.strip():
            continue
        for excerpt in extract_script_excerpts(
            script, max_per_script=max_per_script, max_words=max_words
        ):
            if not passes_filters(excerpt, min_words, max_words):
                continue
            prompt = script_excerpt_prompt(name.rsplit("_", 1)[0])
            pairs.append(row_pair(prompt, excerpt))
            if len(pairs) >= max_pairs:
                break
    return pairs


def strip_dialogue_plain(text: str) -> str:
    """Heuristic: keep scene headings and action; drop ALL-CAPS character cues and dialogue."""
    lines = text.splitlines()
    action: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            if action and action[-1] != "":
                action.append("")
            continue
        if s.startswith("(") and s.endswith(")"):
            continue
        if re.match(r"^(INT\.|EXT\.|INT/EXT|I/E\.)", s, re.I):
            action.append(s)
            continue
        if len(s) < 40 and s.isupper() and " " not in s.strip():
            continue
        if len(s) < 55 and s.isupper():
            continue
        action.append(s)
    blob = re.sub(r"\n{3,}", "\n\n", "\n".join(action)).strip()
    return blob


def chunk_manual_text(text: str, min_words: int, max_words: int) -> list[str]:
    text = strip_dialogue_plain(text)
    if word_count(text) < min_words:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buf: list[str] = []
    for para in paragraphs:
        buf.append(para)
        blob = "\n\n".join(buf)
        wc = word_count(blob)
        if wc >= min_words:
            chunks.append(clamp_words(blob, max_words))
            buf = []
    if buf:
        blob = "\n\n".join(buf)
        if word_count(blob) >= min_words:
            chunks.append(clamp_words(blob, max_words))
    return chunks


def pairs_from_manual(
    filt: str,
    max_pairs: int,
    min_words: int,
    max_words: int,
) -> list[dict]:
    dirs: list[tuple[Path, str]] = []
    if filt in ("welles", "all"):
        dirs.append((WELLES_DIR, "welles"))
    if filt in ("a24", "all"):
        dirs.append((A24_DIR, "a24"))

    pairs: list[dict] = []
    for directory, label in dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*")):
            if path.suffix.lower() not in (".txt", ".md") or path.name == "README.md":
                continue
            raw = path.read_text(encoding="utf-8", errors="ignore")
            title = path.stem.replace("_", " ")
            for chunk in chunk_manual_text(raw, min_words, max_words):
                if has_cjk(chunk) or looks_hype(chunk):
                    continue
                prompt = (
                    f"{WRITE}Deliver prose in screenplay staging register — angles, light, doorways — "
                    f"without quoted dialogue. Manual {label} drop: {title!r}."
                )
                pairs.append(row_pair(prompt, chunk))
                if len(pairs) >= max_pairs:
                    return pairs
    return pairs


def pairs_from_movies_hf(
    filt: str,
    max_pairs: int,
    scripts_cap: int,
    min_words: int,
    max_words: int,
) -> list[dict]:
    """Opt-in: IsmaelMousa/movies — action-only chunks after strip_dialogue_plain."""
    ds = load_dataset(MOVIES_DS, split="train", streaming=True)
    pairs: list[dict] = []
    scanned = 0
    for ex in ds:
        if len(pairs) >= max_pairs:
            break
        name = (ex.get("Name") or "Unknown").strip()
        if filt != "all" and not matches_filter(name.lower().replace(" ", "_") + "_0000", filt):
            # movies dataset has no year — loose title match
            lname = name.lower()
            if filt == "welles" and not any(k.split("_")[0] in lname for k in WELLES_MOVIESUM_KEYS):
                continue
            if filt == "a24" and not any(k.split("_")[0] in lname for k in A24_MOVIESUM_KEYS):
                continue
        scanned += 1
        if scanned > scripts_cap:
            break
        script = ex.get("Script") or ""
        for chunk in chunk_manual_text(script, min_words, max_words):
            if not passes_filters(chunk, min_words, max_words):
                continue
            prompt = script_excerpt_prompt(name)
            pairs.append(row_pair(prompt, chunk))
            if len(pairs) >= max_pairs:
                break
    return pairs


def build_pairs(args: argparse.Namespace) -> list[dict]:
    pairs: list[dict] = []
    if args.dataset == "moviesum":
        pairs.extend(
            pairs_from_moviesum(
                args.filter,
                args.max_pairs,
                args.scripts_cap,
                args.min_words,
                args.max_words,
                args.max_per_script,
            )
        )
    elif args.dataset == "movies":
        pairs.extend(
            pairs_from_movies_hf(
                args.filter,
                args.max_pairs,
                args.scripts_cap,
                args.min_words,
                args.max_words,
            )
        )
    elif args.dataset == "manual":
        pairs.extend(
            pairs_from_manual(args.filter, args.max_pairs, args.min_words, args.max_words)
        )
    return pairs[: args.max_pairs]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest script staging excerpts for Welles SFT.")
    parser.add_argument(
        "--dataset",
        choices=DATASETS,
        default="moviesum",
        help="HF MovieSum, opt-in IsmaelMousa/movies, or manual drop dirs.",
    )
    parser.add_argument(
        "--filter",
        choices=("welles", "a24", "all"),
        default="welles",
        help="Title filter for HF rows; manual uses welles/ and/or a24/ dirs.",
    )
    parser.add_argument("--max-pairs", type=int, default=30, help="Cap output JSONL pairs.")
    parser.add_argument("--scripts-cap", type=int, default=400, help="Max HF scripts scanned.")
    parser.add_argument("--max-per-script", type=int, default=2, help="Excerpts per screenplay.")
    parser.add_argument("--min-words", type=int, default=25)
    parser.add_argument("--max-words", type=int, default=150)
    parser.add_argument("--out", "-o", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pairs = build_pairs(args)
    print(
        f"Script ingest: {len(pairs)} pairs "
        f"(dataset={args.dataset}, filter={args.filter}, cap={args.max_pairs})"
    )
    if args.dry_run:
        for sample in pairs[:3]:
            print("--- prompt ---")
            print(sample["prompt"][:200], "...")
            print("--- words ---", word_count(sample["completion"]))
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for item in pairs:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()