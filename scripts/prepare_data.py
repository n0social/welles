"""Build Welles SFT JSONL: gold voice heavy, style samples, lightly capped LongWriter.

LongWriter teaches length. Gold + style teach Welles. Run on any machine with internet.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from datasets import load_dataset

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
    parser.add_argument("--english-only", action="store_true", default=True)
    parser.add_argument("--include-companions", action="store_true", default=False)
    parser.add_argument("--include-legacy-gold", action="store_true", default=False)
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

    # 3) Optional companions (argument muscle — off by default for voice-first v2)
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

    # 4) LongWriter — length only, lightly capped
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
