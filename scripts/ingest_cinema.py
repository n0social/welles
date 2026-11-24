"""Ingest cinema-adjacent Hugging Face data into Welles SFT prompt/completion pairs."""

from __future__ import annotations

import argparse
import json
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "ingest" / "cinema_pairs.jsonl"

WIKI_DS = "vishnupriyavr/wiki-movie-plots-with-summaries"
MOVIESUM_DS = "rohitsaxena/MovieSum"

WRITE = "WRITE. New prose in Welles's voice.\n\n"


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def looks_hype(text: str) -> bool:
    lowered = text.lower()
    banned = (
        "believe in yourself",
        "you are enough",
        "your journey",
        "unlock your potential",
        "life will be better",
        "positive affirmation",
        "manifest",
    )
    return any(phrase in lowered for phrase in banned)


def word_count(text: str) -> int:
    return len(text.split())


def clamp_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def passes_filters(text: str, min_words: int, max_words: int) -> bool:
    if not text or not text.strip():
        return False
    if has_cjk(text) or looks_hype(text):
        return False
    wc = word_count(text)
    return min_words <= wc <= max_words


def row_pair(prompt: str, completion: str) -> dict:
    return {"prompt": prompt.strip(), "completion": completion.strip()}


def load_pairs(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    out: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        out.append((item["prompt"], item["completion"]))
    return out


def wiki_prompt(title: str, year: int | str, director: str, genre: str, variant: int) -> str:
    meta = f'"{title}" ({year})'
    if director and director.lower() != "unknown":
        meta += f", director: {director}"
    if genre:
        meta += f", genre: {genre}"

    if variant % 2 == 0:
        return (
            f"{WRITE}Compose a cinematic prose passage — concrete staging first, then the naming sentence. "
            f"Film: {meta}. No bullet lists."
        )
    return (
        f"{WRITE}Describe the opening movement of this story as if narrating for radio, then for camera. "
        f"Film: {meta}."
    )


def moviesum_summary_prompt(movie_name: str, variant: int) -> str:
    if variant % 2 == 0:
        return (
            f"{WRITE}Turn this film's situation into Welles-register narration — rooms, light, pause. "
            f"Title: {movie_name!r}."
        )
    return (
        f"{WRITE}Narrate the story's first reversals as if addressing a dark theater and a live microphone. "
        f"Title: {movie_name!r}."
    )


def script_excerpt_prompt(movie_name: str) -> str:
    return (
        f"{WRITE}Deliver prose in screenplay staging register — angles, light, doorways — without quoted dialogue. "
        f"Source film: {movie_name!r}."
    )


def extract_script_excerpts(script_xml: str, max_per_script: int = 2, max_words: int = 120) -> list[str]:
    """Pull stage direction / scene description only (skip dialogue)."""
    try:
        root = ET.fromstring(script_xml)
    except ET.ParseError:
        return []

    excerpts: list[str] = []
    for scene in root.findall(".//scene"):
        if len(excerpts) >= max_per_script:
            break
        parts: list[str] = []
        for tag in ("stage_direction", "scene_description"):
            node = scene.find(tag)
            if node is not None and node.text:
                parts.append(node.text.strip())
        if not parts:
            continue
        chunk = " ".join(parts)
        chunk = re.sub(r"\s+", " ", chunk)
        if word_count(chunk) < 25:
            continue
        excerpts.append(clamp_words(chunk, max_words))
    return excerpts


def iter_wiki_plots(
    max_rows: int,
    min_words: int,
    max_words: int,
    welles_boost: int,
    shard_index: int,
    shard_count: int,
    seed: int,
):
    ds = load_dataset(WIKI_DS, split="train", streaming=True)
    welles_rows: list[dict] = []
    other_rows: list[dict] = []

    for i, ex in enumerate(ds):
        if shard_count > 1 and i % shard_count != shard_index:
            continue
        plot = (ex.get("Plot") or "").strip()
        if not plot:
            continue
        plot = clamp_words(plot, max_words)
        if not passes_filters(plot, min_words, max_words):
            continue
        director = (ex.get("Director") or "").strip()
        row = {
            "plot": plot,
            "title": (ex.get("Title") or "Untitled").strip(),
            "year": ex.get("Release Year") or "",
            "director": director,
            "genre": (ex.get("Genre") or "").strip(),
        }
        if director and "welles" in director.lower():
            welles_rows.append(row)
        else:
            other_rows.append(row)

    rng = random.Random(seed)
    rng.shuffle(welles_rows)
    rng.shuffle(other_rows)

    boosted = welles_rows[:welles_boost]
    need = max(0, max_rows - len(boosted))
    boosted.extend(other_rows[:need])
    return boosted[:max_rows]


def pairs_from_wiki(
    max_rows: int,
    min_words: int,
    max_words: int,
    welles_boost: int,
    shard_index: int,
    shard_count: int,
    seed: int,
) -> list[dict]:
    rows = iter_wiki_plots(
        max_rows, min_words, max_words, welles_boost, shard_index, shard_count, seed
    )
    pairs: list[dict] = []
    for i, row in enumerate(rows):
        prompt = wiki_prompt(row["title"], row["year"], row["director"], row["genre"], i)
        pairs.append(row_pair(prompt, row["plot"]))
    return pairs


def pairs_from_moviesum_summaries(
    max_rows: int,
    min_words: int,
    max_words: int,
    seed: int,
) -> list[dict]:
    ds = load_dataset(MOVIESUM_DS, split="train", streaming=True)
    rng = random.Random(seed)
    pairs: list[dict] = []
    for ex in ds:
        summary = (ex.get("summary") or "").strip()
        summary = clamp_words(summary, max_words)
        if not passes_filters(summary, min_words, max_words):
            continue
        name = (ex.get("movie_name") or "Unknown").strip()
        prompt = moviesum_summary_prompt(name, rng.randint(0, 99))
        pairs.append(row_pair(prompt, summary))
        if len(pairs) >= max_rows:
            break
    return pairs


def pairs_from_moviesum_scripts(
    max_excerpts: int,
    max_words: int,
    scripts_cap: int,
    seed: int,
) -> list[dict]:
    ds = load_dataset(MOVIESUM_DS, split="train", streaming=True)
    rng = random.Random(seed)
    pairs: list[dict] = []
    seen_scripts = 0
    for ex in ds:
        if seen_scripts >= scripts_cap:
            break
        seen_scripts += 1
        script = ex.get("script") or ""
        name = (ex.get("movie_name") or "Unknown").strip()
        for excerpt in extract_script_excerpts(script, max_per_script=2, max_words=max_words):
            prompt = script_excerpt_prompt(name)
            pairs.append(row_pair(prompt, excerpt))
            if len(pairs) >= max_excerpts:
                return pairs
    return pairs


def build_pairs(args: argparse.Namespace) -> list[dict]:
    pairs: list[dict] = []
    if args.max_wiki > 0:
        pairs.extend(
            pairs_from_wiki(
                args.max_wiki,
                args.min_words,
                args.max_words,
                args.welles_boost,
                args.shard_index,
                args.shard_count,
                args.seed,
            )
        )
    if args.max_moviesum > 0:
        pairs.extend(
            pairs_from_moviesum_summaries(
                args.max_moviesum,
                args.min_words,
                args.max_words,
                args.seed + 1,
            )
        )
    if args.include_script_excerpts and args.max_script_excerpts > 0:
        pairs.extend(
            pairs_from_moviesum_scripts(
                args.max_script_excerpts,
                min(args.max_words, 150),
                args.scripts_cap,
                args.seed + 2,
            )
        )
    return pairs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest HF cinema data for Welles SFT.")
    parser.add_argument("--max-wiki", type=int, default=400, help="Max wiki plot pairs.")
    parser.add_argument("--max-moviesum", type=int, default=40, help="Max MovieSum summary pairs.")
    parser.add_argument("--welles-boost", type=int, default=8, help="Minimum Welles-directed wiki rows.")
    parser.add_argument("--min-words", type=int, default=80)
    parser.add_argument("--max-words", type=int, default=550)
    parser.add_argument("--include-script-excerpts", action="store_true", default=False)
    parser.add_argument("--max-script-excerpts", type=int, default=0)
    parser.add_argument("--scripts-cap", type=int, default=80, help="Movie scripts scanned for excerpts.")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", "-o", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true", help="Compute pairs but do not write JSONL.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pairs = build_pairs(args)
    print(
        f"Cinema ingest: {len(pairs)} pairs "
        f"(wiki≤{args.max_wiki}, moviesum≤{args.max_moviesum}, "
        f"script_excerpts={args.include_script_excerpts})"
    )
    if args.dry_run:
        for sample in pairs[:3]:
            print("--- sample prompt ---")
            print(sample["prompt"][:220], "...")
            print("--- completion words ---", word_count(sample["completion"]))
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for item in pairs:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()