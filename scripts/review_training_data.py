"""Review script corpus and train.jsonl before Colab — stats, samples, sanity checks."""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PAIRS = ROOT / "data" / "ingest" / "script_pairs.jsonl"
TRAIN = ROOT / "data" / "train.jsonl"


def task_type(prompt: str) -> str:
    head = prompt.strip().split("\n", 1)[0]
    if head.startswith("SCREENPLAY."):
        if "Continue" in prompt[:120]:
            return "continue"
        if "next scene" in prompt.lower() or "Previous scene" in prompt:
            return "bridge"
        return "verbatim"
    if head.startswith("COMPOSE."):
        return "compose"
    if head.startswith("STRUCTURE."):
        return "structure"
    if head.startswith("WRITE."):
        return "write"
    if head.startswith("REWRITE."):
        return "rewrite"
    if head.startswith("STAGE."):
        return "stage"
    return "other"


def word_count(text: str) -> int:
    return len(text.split())


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def load_pairs(path: Path) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for row in load_jsonl(path):
        if "messages" in row:
            user = assistant = ""
            for t in row["messages"]:
                if t.get("role") == "user":
                    user = t.get("content", "")
                elif t.get("role") == "assistant":
                    assistant = t.get("content", "")
            out.append((user, assistant))
        else:
            out.append((row.get("prompt", ""), row.get("completion", "")))
    return out


def analyze_pairs(pairs: list[tuple[str, str]], label: str) -> dict:
    tasks = Counter()
    prompt_wc: list[int] = []
    comp_wc: list[int] = []
    kane = 0
    empty = 0
    very_short = 0
    for prompt, comp in pairs:
        if not prompt.strip() or not comp.strip():
            empty += 1
            continue
        tasks[task_type(prompt)] += 1
        pw, cw = word_count(prompt), word_count(comp)
        prompt_wc.append(pw)
        comp_wc.append(cw)
        if cw < 15:
            very_short += 1
        blob = (prompt + comp).lower()
        if "citizen kane" in blob or "citizen-kane" in blob:
            kane += 1

    def pct(xs: list[int], p: float) -> int:
        if not xs:
            return 0
        xs = sorted(xs)
        i = min(len(xs) - 1, int(len(xs) * p / 100))
        return xs[i]

    return {
        "label": label,
        "rows": len(pairs),
        "empty": empty,
        "very_short_completion": very_short,
        "kane_mentions": kane,
        "tasks": dict(tasks),
        "prompt_words_p50": pct(prompt_wc, 50),
        "prompt_words_p90": pct(prompt_wc, 90),
        "completion_words_p50": pct(comp_wc, 50),
        "completion_words_p90": pct(comp_wc, 90),
        "completion_words_max": max(comp_wc) if comp_wc else 0,
    }


def print_samples(pairs: list[tuple[str, str]], n: int, seed: int, filter_task: str | None) -> list[str]:
    lines: list[str] = []
    pool = [(p, c) for p, c in pairs if not filter_task or task_type(p) == filter_task]
    random.seed(seed)
    for prompt, comp in random.sample(pool, min(n, len(pool))):
        tt = task_type(prompt)
        lines.append(f"### Sample ({tt})\n")
        lines.append("**Prompt (trimmed):**\n")
        lines.append("```\n" + prompt[:600] + ("…" if len(prompt) > 600 else "") + "\n```\n")
        lines.append("**Completion (trimmed):**\n")
        lines.append("```\n" + comp[:800] + ("…" if len(comp) > 800 else "") + "\n```\n")
    return lines


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--script-pairs", type=Path, default=SCRIPT_PAIRS)
    p.add_argument("--train", type=Path, default=TRAIN)
    p.add_argument("--samples", type=int, default=3)
    p.add_argument("--out", type=Path, default=ROOT / "data" / "ingest" / "corpus_review.md")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    script_pairs = load_pairs(args.script_pairs)
    train_pairs = load_pairs(args.train)

    stats_script = analyze_pairs(script_pairs, "script_pairs.jsonl")
    stats_train = analyze_pairs(train_pairs, "train.jsonl")

    # train mix: approximate tier from prompt
    train_tiers = Counter()
    for prompt, _ in train_pairs:
        tt = task_type(prompt)
        if tt in ("verbatim", "continue", "compose", "bridge", "structure"):
            train_tiers["script_tasks"] += 1
        elif prompt.startswith("WRITE.") and "Welles's voice" in prompt:
            if "screenplay staging" in prompt:
                train_tiers["script_staging_legacy"] += 1
            elif "Gold" not in prompt:
                train_tiers["welles_gold_or_write"] += 1
            else:
                train_tiers["welles_gold_or_write"] += 1
        elif "REWRITE" in prompt:
            train_tiers["welles_gold"] += 1
        elif "CONTINUE" in prompt:
            train_tiers["welles_gold"] += 1
        elif "cinema" in prompt.lower() or "film" in prompt.lower():
            train_tiers["cinema"] += 1
        else:
            train_tiers["other"] += 1

    md: list[str] = [
        "# Training data review (pre-Colab)\n",
        "Auto-generated by `scripts/review_training_data.py`. Regenerate after `build_script_corpus.py`.\n",
        "## Summary\n",
        "| File | Rows | Empty | Very short completions (<15w) | Kane-tagged rows |\n",
        "|------|-----:|------:|-----------------------------:|-----------------:|\n",
        f"| script_pairs | {stats_script['rows']} | {stats_script['empty']} | "
        f"{stats_script['very_short_completion']} | {stats_script['kane_mentions']} |\n",
        f"| train.jsonl | {stats_train['rows']} | {stats_train['empty']} | "
        f"{stats_train['very_short_completion']} | {stats_train['kane_mentions']} |\n",
        "\n## Script task mix (`script_pairs.jsonl`)\n",
    ]
    for k, v in sorted(stats_script["tasks"].items(), key=lambda x: -x[1]):
        pct = 100 * v / max(1, stats_script["rows"])
        md.append(f"- **{k}**: {v} ({pct:.1f}%)\n")

    md.append("\n## Length (words)\n")
    md.append(
        f"- Script pairs — prompt p50/p90: {stats_script['prompt_words_p50']}/{stats_script['prompt_words_p90']}; "
        f"completion p50/p90/max: {stats_script['completion_words_p50']}/{stats_script['completion_words_p90']}/"
        f"{stats_script['completion_words_max']}\n"
    )
    md.append(
        f"- Train — completion p50/p90/max: {stats_train['completion_words_p50']}/"
        f"{stats_train['completion_words_p90']}/{stats_train['completion_words_max']}\n"
    )

    md.append("\n## `train.jsonl` mix (approximate)\n")
    for k, v in sorted(train_tiers.items(), key=lambda x: -x[1]):
        md.append(f"- {k}: {v}\n")

    md.append(
        "\n## Adequacy checklist\n"
        "- [ ] Kane rows present and boosted (search `citizen kane` count above).\n"
        "- [ ] `compose` + `verbatim` teach format; `continue` + `bridge` teach sequence.\n"
        "- [ ] Completion p90 under ~400 words fits `max_length=2048` in train.py.\n"
        "- [ ] Skim samples below — dialogue present in verbatim/continue, not only STRUCTURE notes.\n"
        "- [ ] Welles gold still in mix (~250+ rows) so desk voice doesn’t drown.\n"
        "\n**Red flags:** empty pairs, all STRUCTURE and no verbatim; completion max > 500 words everywhere; "
        "no Kane after boosting.\n"
    )

    md.append("\n## Random samples (script_pairs)\n")
    md.extend(print_samples(script_pairs, args.samples, 42, None))
    md.append("\n### Kane-filtered\n")
    kane_pool = [(p, c) for p, c in script_pairs if "citizen kane" in (p + c).lower()]
    if kane_pool:
        md.extend(print_samples(kane_pool, min(2, args.samples), 7, None))
    else:
        md.append("*No Kane-tagged rows found.*\n")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(md), encoding="utf-8")

    print(json.dumps({"script": stats_script, "train": stats_train, "report": str(args.out)}, indent=2))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()