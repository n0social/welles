"""Ingest screenplay staging text for Welles SFT — HF caps + manual drop dirs.

Default: MovieSum XML stage directions / scene descriptions only (no dialogue).
See data/ingest/script_sources.md for filmography, A24 findings, Script Slug / Cole Haddon
manual PDF workflow, and legal warnings. Title metadata: scripts/ingest_a24_metadata.py.
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

# MovieSum `movie_name` is `Title_YYYY`. Prefer exact keys — loose substrings matched too many "Mr.*" titles.
WELLES_MOVIESUM_KEYS = (
    "citizen_kane_1941",
    "the_magnificent_ambersons_1942",
    "journey_into_fear_1943",
    "the_stranger_1946",
    "the_lady_from_shanghai_1947",
    "macbeth_1948",
    "othello_1952",
    "mr_arkadin_1955",
    "touch_of_evil_1958",
    "the_trial_1962",
    "chimes_at_midnight_1965",
    "the_immortal_story_1968",
    "f_for_fake_1973",
    "filming_othello_1978",
    "the_other_side_of_the_wind_2018",
    "too_much_johnson_1938",
)

WELLES_TITLES_JSON = ROOT / "data" / "ingest" / "welles_titles.json"

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

A24_TITLES_JSON = ROOT / "data" / "ingest" / "a24_titles.json"


def _title_json_keys(path: Path, static_keys: tuple[str, ...]) -> tuple[str, ...]:
    keys = list(static_keys)
    if not path.exists():
        return tuple(keys)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return tuple(keys)
    for row in payload.get("titles", []):
        slug = (row.get("title_slug") or "").strip()
        year = str(row.get("release_year") or "").strip()
        title = (row.get("title") or "").strip()
        if title and year:
            keys.append(f"{title}_{year}")
        if slug and year:
            keys.append(f"{slug}_{year}")
        elif slug:
            keys.append(slug)
    return tuple(dict.fromkeys(keys))


def welles_filter_keys() -> tuple[str, ...]:
    """Static MovieSum keys + optional rows from data/ingest/welles_titles.json."""
    return _title_json_keys(WELLES_TITLES_JSON, WELLES_MOVIESUM_KEYS)


def a24_filter_keys() -> tuple[str, ...]:
    """Static MovieSum keys + optional rows from data/ingest/a24_titles.json."""
    return _title_json_keys(A24_TITLES_JSON, A24_MOVIESUM_KEYS)


WRITE = "WRITE. New prose in Welles's voice.\n\n"

STAGE_A24 = (
    "STAGE. Restage this scene direction in Orson Welles's cinematic prose — "
    "deep space, theatrical lighting, deliberate camera rhythm. "
    "Keep slugline logic; no contemporary indie dialogue tone.\n\n"
)

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
    script_excerpt_prompt,
    word_count,
)


def row_pair(
    prompt: str,
    completion: str,
    *,
    source_studio: str | None = None,
    source_title: str | None = None,
    boosted: bool = False,
) -> dict:
    item: dict = {"prompt": prompt.strip(), "completion": completion.strip()}
    if source_studio:
        item["source_studio"] = source_studio
    if source_title:
        item["source_title"] = source_title
    if boosted:
        item["boosted"] = True
    return item


def _norm_boost_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def title_matches_boost(title: str, boost_titles: tuple[str, ...]) -> bool:
    norm = _norm_boost_title(title)
    for raw in boost_titles:
        needle = _norm_boost_title(raw)
        if not needle:
            continue
        if needle in norm or norm in needle:
            return True
    return False


def apply_boost_pairs(
    pairs: list[dict], boost_titles: tuple[str, ...], boost_repeat: int
) -> list[dict]:
    """Duplicate matching pairs (by source_title or prompt film name) boost_repeat times."""
    if boost_repeat <= 1 or not boost_titles:
        return pairs
    extra: list[dict] = []
    for item in pairs:
        title = item.get("source_title") or ""
        if not title and "Source film:" in item.get("prompt", ""):
            m = re.search(r"Source film:\s*'([^']+)'", item["prompt"])
            if m:
                title = m.group(1)
        if title_matches_boost(title, boost_titles):
            for _ in range(boost_repeat - 1):
                dup = dict(item)
                dup["boosted"] = True
                extra.append(dup)
    return pairs + extra

DATASETS = ("moviesum", "movies", "manual")


def _norm_title(name: str) -> str:
    return re.sub(r"\s+", "_", name.strip().lower())


def matches_filter(movie_name: str, filt: str) -> bool:
    name = _norm_title(movie_name)
    if filt == "all":
        return True
    keys = welles_filter_keys() if filt == "welles" else a24_filter_keys()
    for key in keys:
        k = _norm_title(key)
        if name == k:
            return True
        if "_" in k:
            title_part, _, year = k.rpartition("_")
            if len(year) == 4 and year.isdigit():
                if name.startswith(f"{title_part}_{year}"):
                    return True
                # MovieSum uses spaces in titles, not underscores
                spaced = f"{title_part.replace('_', ' ')}_{year}"
                if name == _norm_title(spaced):
                    return True
            elif not year.isdigit() and k in name:
                # Legacy key without a year suffix
                if k in name:
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
            title = name.rsplit("_", 1)[0]
            prompt = script_excerpt_prompt(title)
            studio = "welles" if filt == "welles" else ("a24" if filt == "a24" else "moviesum")
            pairs.append(
                row_pair(
                    prompt,
                    excerpt,
                    source_studio=studio,
                    source_title=title,
                )
            )
            if len(pairs) >= max_pairs:
                break
    return pairs


SCENE_HEADING = re.compile(r"^(INT\.|EXT\.|INT/EXT|I/E\.)", re.I)


def chunk_screenplay_full(
    text: str,
    min_words: int,
    max_words: int,
    *,
    keep_dialogue: bool = True,
    max_chunks: int = 0,
) -> list[str]:
    """Split a screenplay into scene-bounded chunks (dialogue kept when keep_dialogue)."""
    body = text if keep_dialogue else strip_dialogue_plain(text)
    if word_count(body) < min_words:
        return []

    scenes: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if SCENE_HEADING.match(stripped):
            if current:
                blob = "\n".join(current).strip()
                if word_count(blob) >= min_words:
                    scenes.append(blob)
            current = [line]
        else:
            current.append(line)
    if current:
        blob = "\n".join(current).strip()
        if word_count(blob) >= min_words:
            scenes.append(blob)

    if not scenes:
        scenes = [body.strip()] if word_count(body) >= min_words else []

    out: list[str] = []
    for scene in scenes:
        if word_count(scene) <= max_words:
            out.append(scene)
        else:
            paras = [p.strip() for p in re.split(r"\n\s*\n", scene) if p.strip()]
            buf: list[str] = []
            for para in paras:
                buf.append(para)
                blob = "\n\n".join(buf)
                if word_count(blob) >= min_words:
                    out.append(clamp_words(blob, max_words))
                    buf = []
            if buf:
                blob = "\n\n".join(buf)
                if word_count(blob) >= min_words:
                    out.append(clamp_words(blob, max_words))
        if max_chunks and len(out) >= max_chunks:
            return out[:max_chunks]
    if max_chunks:
        return out[:max_chunks]
    return out


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


SCREENPLAY_BLOCK = (
    "SCREENPLAY. Full scene block — keep industry format: slugline, action, character cues, dialogue.\n\n"
)


def pairs_from_manual(
    filt: str,
    max_pairs: int,
    min_words: int,
    max_words: int,
    *,
    screenplay_mode: str = "staging",
    keep_dialogue: bool = True,
    max_chunks_per_file: int = 0,
) -> list[dict]:
    dirs: list[tuple[Path, str]] = []
    if filt in ("welles", "all"):
        dirs.append((WELLES_DIR, "welles"))
    if filt in ("a24", "all"):
        dirs.append((A24_DIR, "a24"))

    pairs: list[dict] = []
    full_mode = screenplay_mode == "full"

    for directory, label in dirs:
        if not directory.exists():
            continue
        paths = sorted(directory.glob("*"))
        if full_mode:
            full_txt = [p for p in paths if p.suffix.lower() == ".txt" and p.stem.endswith("_full")]
            other = [
                p
                for p in paths
                if p.suffix.lower() in (".txt", ".md")
                and p.name != "README.md"
                and not p.stem.endswith("_excerpt")
                and p not in full_txt
            ]
            paths = full_txt + other
        for path in paths:
            if path.suffix.lower() not in (".txt", ".md") or path.name == "README.md":
                continue
            if path.stem.endswith("_excerpt") and full_mode:
                continue
            raw = path.read_text(encoding="utf-8", errors="ignore")
            if raw.startswith("# Staging excerpts"):
                raw = raw.split("\n\n", 1)[-1] if "\n\n" in raw else raw
            title = path.stem.replace("_full", "").replace("_excerpt", "").replace("_", " ")

            if full_mode:
                chunks = chunk_screenplay_full(
                    raw,
                    min_words,
                    max_words,
                    keep_dialogue=keep_dialogue,
                    max_chunks=max_chunks_per_file,
                )
            else:
                chunks = chunk_manual_text(raw, min_words, max_words)
                if max_chunks_per_file:
                    chunks = chunks[:max_chunks_per_file]

            for scene_i, chunk in enumerate(chunks, start=1):
                if has_cjk(chunk) or looks_hype(chunk):
                    continue
                if full_mode:
                    prompt = f"{SCREENPLAY_BLOCK}Title: {title!r}. Scene {scene_i}."
                elif label == "a24":
                    prompt = f"{STAGE_A24}Source excerpt: {title!r}."
                else:
                    prompt = (
                        f"{WRITE}Deliver prose in screenplay staging register — angles, light, doorways — "
                        f"without quoted dialogue. Manual welles drop: {title!r}."
                    )
                pairs.append(
                    row_pair(
                        prompt,
                        chunk,
                        source_studio=label,
                        source_title=title,
                    )
                )
                if max_pairs and len(pairs) >= max_pairs:
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
            if filt == "welles" and not any(k.split("_")[0] in lname for k in welles_filter_keys()):
                continue
            if filt == "a24" and not any(k.split("_")[0] in lname for k in a24_filter_keys()):
                continue
        scanned += 1
        if scanned > scripts_cap:
            break
        script = ex.get("Script") or ""
        for chunk in chunk_manual_text(script, min_words, max_words):
            if not passes_filters(chunk, min_words, max_words):
                continue
            prompt = script_excerpt_prompt(name)
            pairs.append(
                row_pair(
                    prompt,
                    chunk,
                    source_studio="movies",
                    source_title=name,
                )
            )
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
            pairs_from_manual(
                args.filter,
                args.max_pairs,
                args.min_words,
                args.max_words,
                screenplay_mode=getattr(args, "screenplay_mode", "staging"),
                keep_dialogue=getattr(args, "keep_dialogue", True),
                max_chunks_per_file=getattr(args, "max_chunks_per_file", 0),
            )
        )
    boost_titles = tuple(getattr(args, "boost_titles", None) or ())
    boost_repeat = int(getattr(args, "boost_repeat", 1) or 1)
    pairs = apply_boost_pairs(pairs, boost_titles, boost_repeat)
    if args.max_pairs <= 0:
        return pairs
    limit = args.max_pairs * boost_repeat if boost_titles and boost_repeat > 1 else args.max_pairs
    return pairs[:limit]


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
    parser.add_argument(
        "--screenplay-mode",
        choices=("staging", "full"),
        default="staging",
        help="staging: action-only excerpts; full: scene chunks with dialogue (manual .txt/_full).",
    )
    parser.add_argument(
        "--keep-dialogue",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Full mode: keep dialogue in chunks (default true).",
    )
    parser.add_argument(
        "--max-chunks-per-file",
        type=int,
        default=0,
        help="0 = all scenes/chunks from each file (full screenplay coverage).",
    )
    parser.add_argument("--out", "-o", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--boost-titles",
        nargs="*",
        default=(),
        metavar="TITLE",
        help='Repeat extra copies of pairs for these titles (e.g. "citizen kane").',
    )
    parser.add_argument(
        "--boost-repeat",
        type=int,
        default=2,
        help="Total weight for boosted titles (2 = one extra copy per matching pair).",
    )
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