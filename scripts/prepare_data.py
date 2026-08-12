"""Build a Welles SFT JSONL from LongWriter-6k plus the Welles system prompt.

LongWriter teaches length. The system prompt teaches voice.
Run this on any machine with internet; it only downloads the dataset.
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


def local_book(glob_pat: str) -> list[Path]:
    return [p for p in ROOT.glob(glob_pat) if p.name != "README.md"]


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


def chunk_manuscript(path: Path, prompt_prefix: str) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "gutenberg" in text[:2000].lower():
        text = strip_gutenberg(text)
    parts: list[tuple[str, str]] = []
    current_title = path.stem.replace("_", " ")
    current: list[str] = []

    def flush() -> None:
        body = "\n".join(current).strip()
        if len(body.split()) >= 250:
            prompt = (
                f"{prompt_prefix} Write a chapter titled {current_title!r}. "
                "Hold one argument to the end. Do not backtrack. No hustle gospel."
            )
            parts.append((prompt, body))

    for line in text.splitlines():
        stripped = line.strip()
        is_heading = (
            stripped.startswith("Chapter ")
            or stripped.startswith("Part ")
            or stripped in {"Preface", "Epilogue", "Legacy and Purpose"}
            or stripped.startswith("The Culture of")
            or stripped.startswith("The Epoch")
            or stripped.startswith("The Age of")
            or stripped.startswith("The Heating")
            or stripped.startswith("The Global Machine")
            or stripped.startswith("The Working Mind")
            or stripped.startswith("The Centurion")
            or stripped.startswith("CHAPTER ")
            or stripped.startswith("Chapter.")
            or stripped.startswith("Reclaiming ")
            or stripped.startswith("The protocol")
            or stripped.startswith("Internal Cooling")
            or stripped.startswith("The Doctrine")
        )
        if is_heading and current:
            flush()
            current = []
            current_title = stripped
        current.append(line)
    flush()
    return parts


def row(system: str, prompt: str, completion: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt.strip()},
            {"role": "assistant", "content": completion.strip()},
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-examples", type=int, default=800)
    parser.add_argument("--min-words", type=int, default=400)
    parser.add_argument("--max-words", type=int, default=4000)
    parser.add_argument("--english-only", action="store_true", default=True)
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "train.jsonl")
    args = parser.parse_args()

    system = SYSTEM_PATH.read_text(encoding="utf-8").strip()
    raw = load_dataset("zai-org/LongWriter-6k", split="train")

    kept = []
    gold_path = ROOT / "data" / "architect_gold.jsonl"
    if gold_path.exists():
        for line in gold_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            kept.append(row(system, item["prompt"], item["completion"]))
        print(f"Added {len(kept)} architect gold tasks (rework / write / complete)")

    books = [
        (
            local_book("*Working Bee*.txt") + style_sample_files(),
            "Book 1, The Working Bee. Heat: labor, extraction, institutions, consequence.",
            "Working Bee",
        ),
        (
            local_book("*Unpaid Hour*.txt"),
            "Book 2, The Unpaid Hour. Cooling: reclaim one hour from the hive as limit, not hustle.",
            "Unpaid Hour",
        ),
        (
            local_book("*Craftsmen*.txt") + local_book("*Craftsman*.txt"),
            "Book 3, The Craftsmen. Making: passion and hobby as creation, not a side hustle.",
            "Craftsmen",
        ),
    ]
    for paths, prefix, label in books:
        before = len(kept)
        for path in paths:
            for prompt, completion in chunk_manuscript(path, prefix):
                kept.append(row(system, prompt, completion))
        print(f"Added {len(kept) - before} examples from {label}")

    companion_prefix = (
        "Write educational labor nonfiction in a stern analytic register. "
        "Explain how wealth, work, and class actually operate."
    )
    companion_count = 0
    for path in companion_manuscripts():
        for prompt, completion in chunk_manuscript(path, companion_prefix):
            kept.append(row(system, prompt, completion))
            companion_count += 1
    print(f"Added {companion_count} examples from companion public-domain works")

    longwriter_cap = args.max_examples
    longwriter_added = 0
    for example in raw:
        if longwriter_added >= longwriter_cap:
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
        kept.append(row(system, prompt, completion))
        longwriter_added += 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for item in kept:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(kept)} examples to {args.out}")


if __name__ == "__main__":
    main()
