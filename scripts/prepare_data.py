"""Build Welles SFT JSONL: gold voice heavy, style samples, cinema + script ingest, capped LongWriter.

LongWriter teaches length. Gold + style teach Welles; cinema/scripts add film/staging substance. Run on any machine with internet.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from datasets import load_dataset

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ingest_cinema import DEFAULT_OUT as CINEMA_CACHE, build_pairs, load_pairs as load_cinema_pairs
from ingest_scripts import DEFAULT_OUT as SCRIPT_CACHE, build_pairs as build_script_pairs

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PATH = ROOT / "prompts" / "welles_system.md"
STYLE_DIR = ROOT / "data" / "style_samples"
COMPANION_DIR = ROOT / "data" / "companion"
WELLES_GOLD = ROOT / "data" / "welles_gold.jsonl"
ARCHITECT_GOLD = ROOT / "data" / "architect_gold.jsonl"


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


def example_text(example: dict) -> tuple[str, str]:
    if "messages" in example and example["messages"]:
        user_parts = []
        assistant_parts = []
        for turn in example["messages"]:
            role = turn.get("role", "")
            content = turn.get("content") or ""
            if role == "user":
                user_parts.append(content)
            elif role == "assistant":
                assistant_parts.append(content)
        return "\n".join(user_parts), "\n".join(assistant_parts)

    prompt = example.get("prompt") or example.get("instruction") or ""
    completion = example.get("response") or example.get("output") or example.get("completion") or ""
    return str(prompt), str(completion)


def strip_gutenberg(text: str) -> str:
    start = text.find("*** START OF THE PROJECT GUTENBERG")
    end = text.find("*** END OF THE PROJECT GUTENBERG")
    if start != -1:
        nl = text.find("\n", start)
        text = text[nl + 1 :] if nl != -1 else text
    if end != -1:
        text = text[:end]
    return text.strip()


def style_sample_files() -> list[Path]:
    return [
        p
        for p in list(STYLE_DIR.glob("*.txt")) + list(STYLE_DIR.glob("*.md"))
        if p.name != "README.md"
    ]


def companion_manuscripts() -> list[Path]:
    if not COMPANION_DIR.exists():
        return []
    return sorted(COMPANION_DIR.glob("*.txt"))


def chunk_prose(path: Path, prompt_prefix: str, min_words: int = 120) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "gutenberg" in text[:2000].lower():
        text = strip_gutenberg(text)

    # Split on markdown headings or blank-line paragraphs for style samples.
    chunks: list[str] = []
    if path.suffix.lower() == ".md":
        parts = []
        current: list[str] = []
        for line in text.splitlines():
            if line.startswith("#") and current:
                parts.append("\n".join(current).strip())
                current = []
                continue
            if line.startswith("#"):
                continue
            current.append(line)
        if current:
            parts.append("\n".join(current).strip())
        chunks = [p for p in parts if p]
    else:
        buf: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            is_heading = (
                stripped.startswith("Chapter ")
                or stripped.startswith("CHAPTER ")
                or stripped.startswith("Part ")
            )
            if is_heading and buf:
                body = "\n".join(buf).strip()
                if len(body.split()) >= min_words:
                    chunks.append(body)
                buf = []
            buf.append(line)
        body = "\n".join(buf).strip()
        if len(body.split()) >= min_words:
            chunks.append(body)

    out: list[tuple[str, str]] = []
    for i, body in enumerate(chunks):
        words = len(body.split())
        if words < min_words:
            continue
        title = path.stem.replace("_", " ")
        prompt = (
            f"{prompt_prefix} Write in this register. Piece {i + 1} from {title!r}. "
            "Hold one image or argument to the end. No chatbot tone."
        )
        out.append((prompt, body))
    return out


def row(system: str, prompt: str, completion: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt.strip()},
            {"role": "assistant", "content": completion.strip()},
        ]
    }


def load_gold_file(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    pairs: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        pairs.append((item["prompt"], item["completion"]))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-examples",
        type=int,
        default=150,
        help="Max LongWriter rows (keep low; gold/style carry the voice).",
    )
    parser.add_argument("--min-words", type=int, default=400)
    parser.add_argument("--max-words", type=int, default=2500)
    parser.add_argument("--gold-repeat", type=int, default=3, help="Repeat each gold pair this many times.")
    parser.add_argument(
        "--citizen-kane-repeat",
        type=int,
        default=1,
        help="Extra passes for script rows whose prompt mentions Citizen Kane (after cache load).",
    )
    parser.add_argument("--english-only", action="store_true", default=True)
    parser.add_argument("--include-companions", action="store_true", default=False)
    parser.add_argument("--include-legacy-gold", action="store_true", default=False)
    parser.add_argument(
        "--max-cinema",
        type=int,
        default=60,
        help="Max cinema-ingest rows included (after --cinema-cache load).",
    )
    parser.add_argument(
        "--cinema-cache",
        type=Path,
        default=CINEMA_CACHE,
        help="JSONL of prompt/completion pairs from scripts/ingest_cinema.py",
    )
    parser.add_argument(
        "--fetch-cinema",
        action="store_true",
        default=False,
        help="Run cinema ingest if cache missing or empty (uses ingest defaults).",
    )
    parser.add_argument(
        "--max-wiki-ingest",
        type=int,
        default=400,
        help="When --fetch-cinema: wiki plot cap for ingest_cinema.py",
    )
    parser.add_argument(
        "--max-moviesum-ingest",
        type=int,
        default=40,
        help="When --fetch-cinema: MovieSum summary cap for ingest_cinema.py",
    )
    parser.add_argument(
        "--max-scripts",
        type=int,
        default=25,
        help="Max script-staging rows from data/ingest/script_pairs.jsonl",
    )
    parser.add_argument(
        "--scripts-cache",
        type=Path,
        default=SCRIPT_CACHE,
        help="JSONL from scripts/ingest_scripts.py",
    )
    parser.add_argument(
        "--fetch-scripts",
        action="store_true",
        default=False,
        help="Run script ingest if cache missing or empty.",
    )
    parser.add_argument(
        "--script-dataset",
        choices=("moviesum", "movies", "manual"),
        default="moviesum",
        help="When --fetch-scripts: HF/manual loader for ingest_scripts.py",
    )
    parser.add_argument(
        "--script-filter",
        choices=("welles", "a24", "all"),
        default="welles",
        help="When --fetch-scripts: title/dir filter",
    )
    parser.add_argument(
        "--max-script-ingest",
        type=int,
        default=30,
        help="When --fetch-scripts: pair cap for ingest_scripts.py (0 = all scene chunks).",
    )
    parser.add_argument(
        "--script-screenplay-mode",
        choices=("staging", "full"),
        default="full",
        help="When --fetch-scripts: full = dialogue + scene tasks from *_full.txt (recommended).",
    )
    parser.add_argument(
        "--script-task-mix",
        type=str,
        default="verbatim,continue,compose,bridge,structure",
        help="Full-mode tasks per scene (see ingest_scripts.py).",
    )
    parser.add_argument(
        "--script-min-words",
        type=int,
        default=None,
        help="Override script chunk min words (full mode default 60).",
    )
    parser.add_argument(
        "--script-max-words",
        type=int,
        default=None,
        help="Override script chunk max words (full mode default 380).",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "train.jsonl")
    args = parser.parse_args()

    system = SYSTEM_PATH.read_text(encoding="utf-8").strip()
    kept: list[dict] = []

    # 1) Welles gold (desk-matched WRITE / REWRITE / CONTINUE) — repeated for weight
    gold = load_gold_file(WELLES_GOLD)
    gold_rows = 0
    for _ in range(max(1, args.gold_repeat)):
        for prompt, completion in gold:
            kept.append(row(system, prompt, completion))
            gold_rows += 1
    print(f"Added {gold_rows} Welles gold rows ({len(gold)} unique × {args.gold_repeat})")

    if args.include_legacy_gold:
        legacy = load_gold_file(ARCHITECT_GOLD)
        for prompt, completion in legacy:
            kept.append(row(system, prompt, completion))
        print(f"Added {len(legacy)} legacy architect gold tasks")

    # 2) Style samples (Welles register excerpts)
    style_prefix = (
        "WRITE. New prose in Welles's voice. "
        "Oratorical, cinematic, deliberate."
    )
    style_count = 0
    for path in style_sample_files():
        for prompt, completion in chunk_prose(path, style_prefix, min_words=40):
            kept.append(row(system, prompt, completion))
            style_count += 1
    print(f"Added {style_count} style-sample chunks")

    # 3) Cinema ingest (HF plots / summaries — capped)
    if args.fetch_cinema and (
        not args.cinema_cache.exists() or args.cinema_cache.stat().st_size == 0
    ):
        import argparse as _ap

        ingest_args = _ap.Namespace(
            max_wiki=args.max_wiki_ingest,
            max_moviesum=args.max_moviesum_ingest,
            welles_boost=8,
            min_words=80,
            max_words=550,
            include_script_excerpts=False,
            max_script_excerpts=0,
            scripts_cap=80,
            shard_index=0,
            shard_count=1,
            seed=42,
        )
        pairs = build_pairs(ingest_args)
        args.cinema_cache.parent.mkdir(parents=True, exist_ok=True)
        with args.cinema_cache.open("w", encoding="utf-8") as handle:
            for item in pairs:
                handle.write(
                    json.dumps(
                        {"prompt": item["prompt"], "completion": item["completion"]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(f"Fetched {len(pairs)} cinema pairs into {args.cinema_cache}")

    cinema_pairs = load_cinema_pairs(args.cinema_cache)
    cinema_added = 0
    for prompt, completion in cinema_pairs[: max(0, args.max_cinema)]:
        if not prompt or not completion:
            continue
        if args.english_only and (has_cjk(prompt) or has_cjk(completion)):
            continue
        if looks_hype(prompt) or looks_hype(completion):
            continue
        kept.append(row(system, prompt, completion))
        cinema_added += 1
    sample_path = ROOT / "data" / "ingest" / "cinema_sample.jsonl"
    if cinema_added == 0 and sample_path.exists():
        for prompt, completion in load_cinema_pairs(sample_path)[: max(0, args.max_cinema)]:
            kept.append(row(system, prompt, completion))
            cinema_added += 1
        if cinema_added:
            print(f"Used {cinema_added} rows from {sample_path} (no cache)")
    elif cinema_added:
        print(f"Added {cinema_added} cinema rows (cap {args.max_cinema})")

    # 3b) Script staging ingest (MovieSum excerpts / manual drops — capped)
    if (
        args.fetch_scripts
        and args.script_dataset == "manual"
        and args.scripts_cache.exists()
        and args.scripts_cache.stat().st_size > 0
    ):
        pass  # use existing corpus; skip rebuild
    elif args.fetch_scripts and (
        not args.scripts_cache.exists() or args.scripts_cache.stat().st_size == 0
    ):
        import argparse as _ap

        full_script = args.script_screenplay_mode == "full"
        script_args = _ap.Namespace(
            dataset=args.script_dataset,
            filter=args.script_filter,
            max_pairs=args.max_script_ingest,
            scripts_cap=400,
            max_per_script=2,
            min_words=args.script_min_words if args.script_min_words is not None else (60 if full_script else 25),
            max_words=args.script_max_words if args.script_max_words is not None else (380 if full_script else 150),
            screenplay_mode=args.script_screenplay_mode,
            keep_dialogue=True,
            max_chunks_per_file=0,
            boost_titles=(),
            boost_repeat=1,
            task_mix=args.script_task_mix,
        )
        script_pairs = build_script_pairs(script_args)
        args.scripts_cache.parent.mkdir(parents=True, exist_ok=True)
        with args.scripts_cache.open("w", encoding="utf-8") as handle:
            for item in script_pairs:
                handle.write(
                    json.dumps(
                        {"prompt": item["prompt"], "completion": item["completion"]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(f"Fetched {len(script_pairs)} script pairs into {args.scripts_cache}")

    script_pairs = load_cinema_pairs(args.scripts_cache)
    script_added = 0

    def _is_kane_script(prompt: str) -> bool:
        return "citizen kane" in prompt.lower()

    def _append_script_row(prompt: str, completion: str) -> None:
        nonlocal script_added
        if not prompt or not completion:
            return
        if args.english_only and (has_cjk(prompt) or has_cjk(completion)):
            return
        if looks_hype(prompt) or looks_hype(completion):
            return
        repeats = max(1, args.citizen_kane_repeat if _is_kane_script(prompt) else 1)
        for _ in range(repeats):
            if args.max_scripts > 0 and script_added >= args.max_scripts:
                return
            kept.append(row(system, prompt, completion))
            script_added += 1

    for prompt, completion in script_pairs:
        if args.max_scripts > 0 and script_added >= args.max_scripts:
            break
        _append_script_row(prompt, completion)
    script_sample = ROOT / "data" / "ingest" / "script_sample.jsonl"
    welles_script_sample = ROOT / "data" / "ingest" / "welles_script_pairs_sample.jsonl"
    if script_added == 0:
        fallbacks: list[Path] = []
        if args.script_filter in ("welles", "all") and welles_script_sample.exists():
            fallbacks.append(welles_script_sample)
        if script_sample.exists():
            fallbacks.append(script_sample)
        for fb in fallbacks:
            for prompt, completion in load_cinema_pairs(fb):
                if args.max_scripts > 0 and script_added >= args.max_scripts:
                    break
                _append_script_row(prompt, completion)
            if args.max_scripts > 0 and script_added >= args.max_scripts:
                break
            if script_added:
                print(f"Used script-staging rows from {fb.name} (no script cache)")
                break
    elif script_added:
        cap = args.max_scripts if args.max_scripts > 0 else "all"
        print(f"Added {script_added} script-staging rows (cap {cap})")

    # 4) Optional companions (argument muscle — off by default for voice-first v2)
    if args.include_companions:
        companion_prefix = (
            "WRITE. New prose in Welles's voice. "
            "Stern analytic register; concrete first, then the naming sentence."
        )
        companion_count = 0
        for path in companion_manuscripts():
            for prompt, completion in chunk_prose(path, companion_prefix, min_words=250):
                kept.append(row(system, prompt, completion))
                companion_count += 1
        print(f"Added {companion_count} companion chunks")

    # 5) LongWriter — length only, lightly capped
    raw = load_dataset("zai-org/LongWriter-6k", split="train")
    longwriter_added = 0
    for example in raw:
        if longwriter_added >= args.max_examples:
            break
        prompt, completion = example_text(example)
        if not prompt or not completion:
            continue
        if args.english_only and (has_cjk(prompt) or has_cjk(completion)):
            continue
        if looks_hype(prompt) or looks_hype(completion):
            continue
        words = len(completion.split())
        if words < args.min_words or words > args.max_words:
            continue
        kept.append(
            row(
                system,
                f"WRITE. New prose in Welles's voice.\n\n{prompt.strip()}",
                completion,
            )
        )
        longwriter_added += 1
    print(f"Added {longwriter_added} LongWriter rows (cap {args.max_examples})")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for item in kept:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(kept)} examples to {args.out}")


if __name__ == "__main__":
    main()
