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

Survey: **2026-11-24** (page fetch + `robots.txt` / `ai.txt` / [Legal ToS](https://www.scriptslug.com/legal)). Neither source grants ML redistribution rights; **this repo does not run site scrapers**.

### [Script Slug](https://www.scriptslug.com/) (`scriptslug.com`)

#### Site structure

| Path | Purpose |
|------|---------|
| `/scripts/studio/a24` | Studio listing (faceted UI; script cards load client-side). |
| `/script/{kebab-title}-{year}` | Per-script page (HTML + embedded PDF viewer; `?page=N` deep links). |
| `/sitemap.xml` | Index of sub-sitemaps: `sitemap-scripts.xml`, `sitemap-studios.xml`, etc. |
| `/craft/`, `/api/`, `/*?q=` | Disallowed for generic crawlers in `robots.txt`. |

Example script URLs (public sitemap pattern, **not bulk-fetched by this repo**):  
`https://www.scriptslug.com/script/materialists-2025`, `…/moonlight-2016`.

#### robots.txt & AI policy

| Document | Key points |
|----------|------------|
| [robots.txt](https://www.scriptslug.com/robots.txt) | Blocks **AI training crawlers** (GPTBot, ClaudeBot, CCBot, …) on `/`. Search-oriented bots allowed with path limits. States scripts are **copyrighted**; Script Slug cannot grant training rights → [ai.txt](https://www.scriptslug.com/ai.txt). |
| [ai.txt](https://www.scriptslug.com/ai.txt) (2026-11-23) | **Training: NOT GRANTED** (PDFs + site copy). Search/citation: allowed with attribution. |
| [Legal ToS](https://www.scriptslug.com/legal) §9 | Prohibits scrapers, crawlers, **systematic download**, and **dataset creation for AI** without written permission. |

#### Use license (humans)

| Aspect | Detail |
|--------|--------|
| **Format** | Searchable **original studio PDFs** (Courier layouts, revision colors, title pages). |
| **Cost** | Free on-site reading/download per [About FAQ](https://www.scriptslug.com/about). |
| **Provenance** | “Found online or provided by users”; fair-use educational framing. |
| **Commercial / training** | FAQ: **no commercial use**; ai.txt denies model training; §2 use license is **personal non-commercial transitory viewing** only. |

#### Repo policy

| Allowed | Not allowed |
|---------|-------------|
| Docs link to studio listing | Automated sitemap/script HTML/PDF download |
| `data/ingest/a24_script_slug_index.json` — **metadata guesses** from AlexPMorton titles (`script_slug_url_verified: false`) | Committing full PDFs or scraped script bodies |
| User drops PDF in `data/scripts/a24/incoming/` → `extract_screenplay_pdf.py` | Bulk sitemap/studio crawls; `ingest_scripts.py` pulling from Script Slug |
| User-operated `download_screenplay_pdf.py` (one URL / queue row) | Committing PDFs or automated dataset builds |

**Safer reads:** studio award PDFs (e.g. [Babygirl on `a24awards.com`](https://a24awards.com/assets/Babygirl-screenplay.pdf)) — still not a training license by default.

### Cole Haddon — [“60 A24 Screenplays to Download and Study”](https://colehaddon.substack.com/p/60-a24-screenplays-to-download-and)

| Aspect | Detail |
|--------|--------|
| **What it is** | Paid Substack post (Jan 2026) curating **60 feature screenplays** A24 released or distributed since ~2012 — editor’s “arthouse gems” list, not a complete studio catalog. |
| **Format** | Outbound **PDF download links** (often awards / studio / third-party hosts). Includes **2025** titles cited in the post (e.g. *The Smashing Machine*, *Eddington*, *Materialists*). |
| **License / training** | Same as any fan/curator list: **personal study links**, not permission to redistribute text or train on verbatim scripts. Paid post does not transfer copyright. |
| **Related** | Cole Haddon’s [“Hundreds of Screenplays”](https://colehaddon.substack.com/p/resource-hundreds-of-screenplays) hub links other themed collections (comedy, horror, women writers, etc.). |

### User-operated “one-by-one” PDF bot (local cache)

The repo ships **`scripts/download_screenplay_pdf.py`** — a **polite, user-operated** helper that fetches **one approved URL at a time** (or one queue row per run). It is **not** a full-site crawler.

| Rule | Detail |
|------|--------|
| **Who runs it** | You, on your machine, after reading Script Slug / Substack terms |
| **What it fetches** | Only `--url` you pass or rows in `data/ingest/a24_download_queue.json` |
| **Where files go** | `data/scripts/a24/incoming/*.pdf` (**gitignored**) |
| **Logs** | `data/ingest/download_log.jsonl` (**gitignored**) |
| **Index scrape** | **`build_a24_slug_index.py` stubs live studio listing parse** (SPA); default rebuilds title→URL guesses from `a24_titles.json` only |

**Legal checklist (before any download):**

1. Personal / education study only — **no** commercial redistribution of PDFs or excerpt text.
2. **Honoring takedowns** — delete local copies if a host or rights holder objects.
3. **Cole Haddon** — paid Substack; paste **direct PDF URLs** you can access into the queue (`pdf_url`), not paywalled HTML.
4. **Hub / commercial weights** — treat downloaded screenplays as **extra risk**: copyrighted dialogue; MovieSum NC may still be safer for training than verbatim PDFs.
5. **Never commit PDFs** to this git repo.

```bash
# Optional: refresh title→Script Slug URL guesses (metadata only, no PDFs)
python3 scripts/scrape_a24_metadata.py
python3 scripts/build_a24_slug_index.py --sync-queue   # fills queue from titles

# One Script Slug title (resolves PDF link from the script page HTML)
python3 scripts/download_screenplay_pdf.py \
  --i-accept-personal-use-only \
  --url "https://www.scriptslug.com/script/moonlight-2016"

# Queue: one item per invocation
python3 scripts/download_screenplay_pdf.py --i-accept-personal-use-only --from-queue

# Queue: up to 5 items, 30s between (still user-operated; max-per-run cap)
python3 scripts/download_screenplay_pdf.py --i-accept-personal-use-only \
  --from-queue --max-per-run 5 --delay 30

# Cole Haddon / award host — direct PDF URL you obtained with subscriber access
python3 scripts/download_screenplay_pdf.py --i-accept-personal-use-only \
  --url "https://example.com/path/to/screenplay.pdf" --out-name "materialists-2025.pdf"

# After download → staging excerpts (dialogue stripped)
python3 scripts/extract_screenplay_pdf.py
python3 scripts/ingest_scripts.py --dataset manual --filter a24
```

### Recommended manual workflow (Sky)

```bash
# 1) Metadata title list (GitHub AlexPMorton fallback; optional Kaggle if creds)
python3 scripts/scrape_a24_metadata.py

# 2) PDFs → incoming/ (manual drop **or** user-operated download bot above)
python3 scripts/extract_screenplay_pdf.py

# 3) Ingest manual drops + optional MovieSum A24 filter
python3 scripts/ingest_scripts.py --dataset manual --filter a24
```

1. **Pick titles** from `a24_titles.json` / `a24_titles.csv` or cross-check `a24_script_slug_index.json` (guessed Script Slug paths — verify in browser).
2. **Obtain PDF** via manual browser save **or** `download_screenplay_pdf.py` (never bulk sitemap/studio crawls in-repo).
3. **extract_screenplay_pdf.py** writes capped staging chunks to `data/scripts/a24/` (dialogue stripped).
4. **`ingest_scripts.py`** merges manual `.txt` into gitignored `script_pairs.jsonl`.
5. Never commit full features; `incoming/*.pdf` is gitignored.

**Linking in docs:** OK to cite Script Slug and Cole Haddon URLs. **Ingesting:** local files only.

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