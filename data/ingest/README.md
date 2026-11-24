# Cinema data ingest (Welles LoRA)

This tier adds **film-adjacent prose** to the SFT mix: plot movement, staging language, and screenplay structure — aligned with Orson Welles’s world (camera, theater, radio oratory), **not** labor/Marxist themes (those belong in the separate `marxism` repo).

Original Welles **quotations** are not harvested here; gold lives in `data/welles_gold.jsonl` and `data/style_samples/`. Ingest favors **paraphrase-style desk tasks** (`WRITE` / `REWRITE` prefixes) over verbatim celebrity quotes.

## Kaggle survey

See **`data/ingest/kaggle_sources.md`** for Orson Welles / A24 / screenplay corpora on Kaggle (no dedicated Welles or A24 script sets; metadata and general script neighbors documented).

## Candidate Hugging Face / public sources

| Dataset | Hub ID | License | Language | Fit for Qwen SFT | Notes |
|--------|--------|---------|----------|------------------|-------|
| Wikipedia movie plots | [`vishnupriyavr/wiki-movie-plots-with-summaries`](https://huggingface.co/datasets/vishnupriyavr/wiki-movie-plots-with-summaries) | CC BY-SA 4.0 | English | **Primary default** | ~35k plots + metadata (title, year, director, genre). Encyclopedic tone → use like companions/style: cinematic *substance* under Welles prompts. Kaggle lineage: [jrobischon/wikipedia-movie-plots](https://www.kaggle.com/jrobischon/wikipedia-movie-plots). |
| MovieSum (summaries) | [`rohitsaxena/MovieSum`](https://huggingface.co/datasets/rohitsaxena/MovieSum) | CC BY-NC 4.0 | English | **Secondary (summary-only)** | Wikipedia-style summaries paired with screenplays. **Non-commercial** license — OK for research / personal training; check before Hub redistribution. |
| MovieSum (screenplays) | same | CC BY-NC 4.0 | English | **Optional excerpts only** | Full scripts are **copyrighted studio works**. Default ingest uses **summaries** and optional **stage-direction / scene-description** snippets (no dialogue). Enable only with `--include-script-excerpts`. |
| MovieSum stats | — | — | — | — | ~2.2k titles; mean script ~34k tokens — too long raw; chunk or summarize. |
| Rotten Tomatoes subset | `cornell-movie-review-data/rotten_tomatoes` | — | English | **Low priority** | Short review blurbs; good for sentiment, weak for cinematography register. Not wired by default. |
| Cornell Movie Dialog | (classic corpus, various mirrors) | Research use | English | **Skip for v1** | Quoted film dialogue → copyright risk for SFT redistribution. |
| WikiPlots (narrative) | various / unmaintained IDs on Hub | varies | English | **Fallback** | Many loader scripts deprecated; prefer wiki-movie-plots HF mirror above. |
| NiklasAbraham MoviePlotEmbeddings | CSV + embeddings on Hub | CC BY-NC 4.0 | English | **Future bulk** | ~92k plots 1930–2024; pull `final_dataset.csv` for large offline ingest (not bundled here). |
| IMSDb / DailyScript (web) | N/A | Copyrighted | English | **Do not ingest verbatim** | Useful for manual study; scripts are not licensed for ML redistribution. |
| Project Gutenberg film essays | e.g. early film criticism | Public domain | English | **Manual companion** | Add excerpts to `data/style_samples/` if needed. |

### Qwen3 SFT fit

- **Chat `messages` format** matches `scripts/prepare_data.py` (system = `prompts/welles_system.md`).
- Prefer **English**, **120–600 word** assistant spans for wiki plots; cap LongWriter separately.
- **Boost Welles-directed rows** when sampling wiki plots (`Director` contains `Welles`).
- NC-licensed MovieSum: keep in training mix for experimentation; document license on model card if weights are published.

## Pipeline layout

```
HF datasets  →  scripts/ingest_cinema.py  →  data/ingest/cinema_pairs.jsonl
                                                      ↓
                                        scripts/prepare_data.py (--max-cinema)
                                                      ↓
                                              data/train.jsonl
```

## Commands

Dry-run (no write; prints planned counts):

```bash
python3 scripts/ingest_cinema.py --dry-run --max-wiki 50 --max-moviesum 10
```

Fetch and cache (starter scale):

```bash
python3 scripts/ingest_cinema.py \
  --max-wiki 400 \
  --max-moviesum 40 \
  --welles-boost 8 \
  -o data/ingest/cinema_pairs.jsonl
```

Optional screenplay staging snippets (no dialogue):

```bash
python3 scripts/ingest_cinema.py --include-script-excerpts --max-script-excerpts 20
```

Merge into training mix (cinema capped so gold dominates):

```bash
python3 scripts/prepare_data.py --max-examples 150 --gold-repeat 3 --max-cinema 60
```

Auto-fetch cinema if cache missing:

```bash
python3 scripts/prepare_data.py --fetch-cinema --max-cinema 60
```

## Filters (ingest)

- English heuristics: no CJK in plot/summary text
- `looks_hype()` banned phrases (shared with `prepare_data.py`)
- Word bounds: `--min-words` / `--max-words` (defaults 80 / 550)
- Skips empty or ultra-short plots

## Scaling to “a ton of” data

1. Run `ingest_cinema.py` on a GPU box with `HF_HOME=./hf_cache` and high `--max-wiki` (e.g. 10k+), shard with `--shard-index` / `--shard-count` (round-robin by row index).
2. Add **NiklasAbraham** CSV plots offline (filter `plot_length_tokens`, genre = drama/noir/documentary).
3. Drop **private** Welles-adjacent pastiche or PD radio transcripts into `data/style_samples/` (highest voice signal).
4. Keep **gold repeat ×3** and `--max-cinema` ≤ ~15–20% of total rows so voice stays Welles not Wikipedia.
5. For commercial release, replace MovieSum (NC) with wiki-only or self-authored pairs.

## Cached files

| Path | In git? |
|------|---------|
| `data/ingest/cinema_pairs.jsonl` | Ignored (large); regenerate with ingest |
| `data/ingest/cinema_sample.jsonl` | Small committed sample for CI/dry checks |