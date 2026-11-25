"""Load external screenplay datasets into Welles prompt/completion pairs."""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
SAMPLES = ROOT / "data" / "ingest" / "external_samples"

THINK_OPEN = "<think>"
THINK_CLOSE = "</think>"

# Categories worth mixing for review / punch-up (skip pure generation bibles for voice-first runs)
DEFAULT_ATUM09_CATEGORIES = frozenset(
    {
        "script_coverage",
        "rewrite_punchup",
        "dialogue_craft",
        "structure_analysis",
        "scene_construction",
    }
)

PUNCHUP_USER_PREFIX = (
    "REWRITE. Punch up in Welles staging register where possible — "
    "keep beats and substance. Sharpen dialogue and image.\n\n"
)
COVERAGE_USER_PREFIX = "REVIEW. Notes and specific fixes; then the improved passage.\n\n"


def _atum09_paths() -> list[Path]:
    train = EXTERNAL / "atum09-screenplay-dataset" / "data" / "train"
    if train.exists():
        return sorted(train.glob("*.jsonl"))
    return sorted(SAMPLES.glob("atum09_*.jsonl"))


def _messages_to_user_assistant(record: dict) -> tuple[str, str] | None:
    msgs = record.get("messages") or []
    user_parts: list[str] = []
    assistant_parts: list[str] = []
    for turn in msgs:
        role = turn.get("role") or turn.get("from")
        content = (turn.get("content") or turn.get("value") or "").strip()
        if not content or role in ("system", "system\n"):
            continue
        if role == "user":
            user_parts.append(content)
        elif role == "assistant":
            assistant_parts.append(content)
    if not user_parts or not assistant_parts:
        return None
    return "\n\n".join(user_parts), "\n\n".join(assistant_parts)


def _wrap_thinking(reasoning: str, visible: str) -> str:
    reasoning = reasoning.strip()
    visible = visible.strip()
    if not reasoning:
        return f"{THINK_OPEN}\n\n{THINK_CLOSE}\n\n{visible}"
    return f"{THINK_OPEN}\n{reasoning}\n{THINK_CLOSE}\n\n{visible}"


def _prefix_prompt(category: str, user: str) -> str:
    cat = (category or "").lower()
    if cat == "rewrite_punchup":
        return PUNCHUP_USER_PREFIX + user
    if cat == "script_coverage":
        return COVERAGE_USER_PREFIX + user
    if cat in ("dialogue_craft", "structure_analysis", "scene_construction"):
        return f"EDIT. {cat.replace('_', ' ')}.\n\n" + user
    return "SCREENPLAY.\n\n" + user


def load_atum09_pairs(
    *,
    categories: set[str] | None = None,
    max_rows: int = 0,
    use_thinking_field: bool = True,
    seed: int = 42,
) -> list[tuple[str, str]]:
    """Pairs: (user prompt, assistant completion) for prepare_data."""
    cats = categories or set(DEFAULT_ATUM09_CATEGORIES)
    paths = _atum09_paths()
    if not paths:
        return []

    rows: list[tuple[str, str, str]] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            cat = (rec.get("category") or "").strip()
            if cat and cat not in cats:
                continue
            parsed = _messages_to_user_assistant(rec)
            if not parsed:
                continue
            user, assistant = parsed
            thinking = (rec.get("thinking") or rec.get("metadata", {}).get("thinking") or "").strip()
            if use_thinking_field and thinking:
                assistant = _wrap_thinking(thinking, assistant)
            prompt = _prefix_prompt(cat, user)
            rows.append((prompt, assistant, cat))

    if max_rows > 0 and len(rows) > max_rows:
        rng = random.Random(seed)
        rows = rng.sample(rows, max_rows)

    return [(p, a) for p, a, _ in rows]


def external_status() -> dict:
    """Paths present for Colab sanity checks."""
    return {
        "atum09_batches": len(_atum09_paths()),
        "inkwell_cases": (EXTERNAL / "inkwell-screenplay-revision-evaluation" / "data" / "cases.jsonl").exists()
        or (SAMPLES / "inkwell_revision_eval.jsonl").exists(),
        "movie_corpus": (EXTERNAL / "kaggle-movie-scripts-corpus" / "screenplay_data").exists(),
    }