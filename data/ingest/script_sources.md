# Screenplay & script sources (Orson Welles + A24)

This document records **research** for the Welles LoRA **script/staging** tier (`scripts/ingest_scripts.py`). It complements plot/summary ingest in [`data/ingest/README.md`](README.md) (`scripts/ingest_cinema.py`).

> **Legal (read first):** Feature-film screenplays are **copyrighted** studio/literary works. Redistribution in a public dataset, Hub model weights, or this git repo generally requires **rights you do not get** from IMSDb, Studioscripts, random PDFs, or Substack “download for study” links. Default automation uses **only**:
>
> - Hugging Face datasets with stated licenses, and then **stage directions / scene descriptions only** (no quoted dialogue) from MovieSum-style XML where possible
> - **Your own** `.txt` / `.md` files in `data/scripts/welles/` or `data/scripts/a24/` that you have the right to use for training (self-authored, licensed, or clearly public domain)
>
> **Do not** commit full Hollywood scripts to git. `data/ingest/script_pairs.jsonl` is gitignored (regenerate locally).

---

## Orson Welles — directed features (priority filmography)

Use these titles when filtering HF rows or naming manual drops. Co-direction / uncredited work is noted.

| Year | Title | Script notes |
|------|-------|----------------|
| 1941 | **Citizen Kane** | Mankiewicz & Welles; RKO. Archetypal staging; **in copyright** (see UIUC surrogate: “In Copyright”). |
| 1942 | **The Magnificent Ambersons** | RKO; truncated in release. |
| 1946 | **The Stranger** | Welles as director/star. |
| 1947 | **The Lady from Shanghai** | Columbia; famous hall-of-mirrors sequence. |
| 1948 | **Macbeth** | Republic (also later re-edit). |
| 1952 | **Othello** | Welles production; long gestation. |
| 1955 | **Mr. Arkadin** / *Confidential Report* | Multiple cuts exist. |
| 1958 | **Touch of Evil** | Universal; opening crane shot. |
| 1962 | **The Trial** | Welles adaptation of Kafka. |
| 1965 | **Chimes at Midnight** | Falstaff / *Henry IV* mashup. |
| 1968 | **The Immortal Story** | TV / short feature. |
| 1973 | **F for Fake** | Essay film; metafiction. |
| 1978 | **Filming Othello** | Documentary / talk. |
| 2018 | **The Other Side of the Wind** | Posthumous completion (Netflix). |

Also: **Too Much Johnson** (1938, unfinished), **Journey into Fear** (1943, co-directed with Norman Foster), extensive **radio** scripts (1930s–40s, many PD-adjacent for research — verify per script).

### Web / archive sources (study only — **not** auto-ingested)

| Source | URL / note | License / risk |
|--------|------------|----------------|
| IMSDb writer index | [imsdb.com/writer.php?w=Orson+Welles](https://imsdb.com/writer.php?w=Orson+Welles) | Fan-hosted **full scripts**; **no** ML redistribution rights. |
| UIUC Digital Collections | [Citizen Kane revised final script (1940)](https://digital.library.illinois.edu/items/fb1e7c00-6ae8-0137-6d00-02d0d7bfd6e4-9) | Marked **In Copyright**. |
| Wellesnet unfilmed index | [wellesnet.com scripts page](https://wellesnet.com/unfilmed-orson-welles-scripts-available-online/) | Points to Scribd PDFs; copyright varies. |

**Manual workflow:** If you lawfully obtain a Welles script (purchase, permission, or PD radio text), place a **redacted excerpt** (staging only, or paraphrase) in `data/scripts/welles/` — see that folder’s README.

---

## A24 — findings (honest)

| Finding | Detail |
|---------|--------|
| **Official A24 screenplay HF dataset** | **None found** (Nov 2025). No studio-published script corpus on the Hub. |
| **A24 metadata only** | Kaggle [A24 Studio movies dataset](https://www.kaggle.com/datasets/sebastiansuliborski/a24-studio-movies-dataset) — titles, budgets, credits; **no screenplay text**. See also **`AlexPMorton/A24-Movies-EDA`** on GitHub (not Kaggle) in [`kaggle_sources.md`](kaggle_sources.md). |
| **Curated blog lists** | e.g. Cole Haddon Substack “60 A24 Screenplays” — **links to PDFs for personal study**; not a license for training redistribution. |
| **MovieSum filter** | Several A24-era titles appear with full scripts (e.g. *Moonlight*, *Lady Bird*, *Hereditary*, *Midsommar*, *Eighth Grade*) — dataset license **CC BY-NC 4.0**; content still **copyright**. Ingest uses **stage-direction excerpts only**. |
| **IsmaelMousa/movies** | 1,172 plain-text scripts, **Apache 2.0** on the *collection*; individual screenplays remain copyrighted. **Not enabled by default** (`--dataset movies` is opt-in and still skips dialogue). |

---

## Script Slug + Cole Haddon (PDF study sources — **manual only**)

Survey: **2026-11-24**. These are the best public **indexes** for A24 screenplay PDFs. Neither grants ML redistribution rights; repo automation must **not** scrape or bulk-download them.

### [Script Slug](https://www.scriptslug.com/) (`scriptslug.com`)

| Aspect | Detail |
|--------|--------|
| **Format** | Searchable **original studio PDFs** (Courier layouts, revision colors, title pages). Browse A24 via [A24 Screenplays](https://www.scriptslug.com/scripts/studio/a24). |
| **Cost** | Free to read/download on site (per [About → FAQ](https://www.scriptslug.com/about)). |
| **Provenance** | “Found online or provided by users”; organized for education. |
| **License / training** | Site states **fair use for education and research only**; **no commercial use** and **no grant of rights**. Honors takedown requests. A24 [Terms of Use](https://a24films.com/terms-of-use) limit official materials to **personal, non-commercial** viewing. |
| **Repo policy** | **Do not** link Script Slug bulk download into `ingest_scripts.py`. **Do not** commit full PDFs/text. Optional: Sky manually opens a title, copies **staging-only** excerpts into `data/scripts/a24/<title_slug>.txt`. |
| **Safer reads** | Studio-posted award-season PDFs (e.g. [Babygirl screenplay on `a24awards.com`](https://a24awards.com/assets/Babygirl-screenplay.pdf)) are **authorized studio copies** for personal study — still **not** a training redistribution license unless A24 says otherwise. |

### Cole Haddon — [“60 A24 Screenplays to Download and Study”](https://colehaddon.substack.com/p/60-a24-screenplays-to-download-and)

| Aspect | Detail |
|--------|--------|
| **What it is** | Paid Substack post (Jan 2026) curating **60 feature screenplays** A24 released or distributed since ~2012 — editor’s “arthouse gems” list, not a complete studio catalog. |
| **Format** | Outbound **PDF download links** (often awards / studio / third-party hosts). Includes **2025** titles cited in the post (e.g. *The Smashing Machine*, *Eddington*, *Materialists*). |
| **License / training** | Same as any fan/curator list: **personal study links**, not permission to redistribute text or train on verbatim scripts. Paid post does not transfer copyright. |
| **Related** | Cole Haddon’s [“Hundreds of Screenplays”](https://colehaddon.substack.com/p/resource-hundreds-of-screenplays) hub links other themed collections (comedy, horror, women writers, etc.). |

### Recommended manual workflow (Sky)

1. **Pick titles** from `data/ingest/a24_titles.csv` (regenerate with `scripts/ingest_a24_metadata.py`) or MovieSum `--filter a24`.
2. **Obtain PDF** yourself via Script Slug, Cole Haddon, `a24awards.com`, or a licensed book — **not** via repo scrapers.
3. Convert locally (`pdftotext`, Acrobat export) to **`.txt`**; strip quoted dialogue if you only want staging register.
4. Drop under `data/scripts/a24/` as `moonlight_2016.txt`, etc. (see folder README).
5. Run `python3 scripts/ingest_scripts.py --dataset manual --filter a24` — ingest applies `strip_dialogue_plain` and word caps; output stays in gitignored `script_pairs.jsonl`.
6. Keep **short excerpts** in git if you must commit examples; never full features.

**Linking in docs:** OK to cite Script Slug and Cole Haddon URLs in this file for humans. **Ingesting:** manual drops only.

---

## Hugging Face dataset search (screenplay-related)

| Hub ID | License | Welles / A24 fit | Wired in `ingest_scripts.py` |
|--------|---------|------------------|------------------------------|
| [`rohitsaxena/MovieSum`](https://huggingface.co/datasets/rohitsaxena/MovieSum) | CC BY-NC 4.0 | **Kane** present; several **A24** titles; most Welles films **absent** | **`moviesum`** (default) |
| [`Francis2003/Movie-O-Label`](https://huggingface.co/datasets/Francis2003/Movie-O-Label) | CC BY-NC 4.0 (MovieSum derived) | Same script text + Oscar labels | Same loader as MovieSum via `--dataset moviesum` |
| [`IsmaelMousa/movies`](https://huggingface.co/datasets/IsmaelMousa/movies) | Apache 2.0 | Generic; filter manually | **`movies`** (opt-in, action-only heuristic) |
| [`vishnupriyavr/wiki-movie-plots-with-summaries`](https://huggingface.co/datasets/vishnupriyavr/wiki-movie-plots-with-summaries) | CC BY-SA 4.0 | Plots only (Welles **director** boost) | Use **`ingest_cinema.py`**, not script tier |

**MovieSum scan (streamed, Nov 2025):** Orson-specific matches essentially **`Citizen Kane_1941`** among canonical titles; A24 examples include **`Moonlight_2016`**, **`Lady Bird_2017`**, **`Hereditary_2018`**, **`Midsommar_2019`**, **`Eighth Grade_2018`**.

---

## Pipeline

```
HF MovieSum (optional)  ─┐
Manual data/scripts/*   ─┼→  scripts/ingest_scripts.py  →  data/ingest/script_pairs.jsonl
                         │
                         └→  scripts/prepare_data.py (--max-scripts)
                                       ↓
                               data/train.jsonl
```

Cinema plots (`cinema_pairs.jsonl`) and script staging (`script_pairs.jsonl`) are **separate caps** so gold voice still dominates.

---

## Commands

```bash
# Welles-biased MovieSum staging excerpts (no dialogue)
python3 scripts/ingest_scripts.py --dataset moviesum --filter welles --max-pairs 20

# A24 titles in MovieSum
python3 scripts/ingest_scripts.py --dataset moviesum --filter a24 --max-pairs 25

# After dropping licensed files into data/scripts/welles/
python3 scripts/ingest_scripts.py --dataset manual --filter welles --max-pairs 50

# Merge (with cinema tier)
python3 scripts/ingest_scripts.py --dataset moviesum --filter all --max-pairs 30
python3 scripts/prepare_data.py --max-cinema 60 --max-scripts 25
```

Auto-fetch when cache missing:

```bash
python3 scripts/prepare_data.py --fetch-scripts --max-scripts 20
```

---

## License summary for trainers

| Source | Train/experiment | Commercial / Hub weights |
|--------|------------------|---------------------------|
| MovieSum excerpts | OK under **CC BY-NC 4.0** (non-commercial) | Verify NC before commercial release |
| Wiki plots (cinema tier) | CC BY-SA 4.0 | Attribution + share-alike considerations |
| Manual drops | Whatever **you** certify | Your responsibility |
| Full scripts from web | **Avoid** verbatim ingest | — |

When publishing a model card, cite MovieSum if used and state **non-commercial** use if NC data is in the mix.