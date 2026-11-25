# Incoming Orson Welles screenplay PDFs

Upload **PDFs you obtained yourself** (UIUC surrogates, licensed scans, radio-script PDFs you have rights to, etc.) to this folder, then run the extract + ingest pipeline.

## Naming

Use **`Title_Year.pdf`** — underscores, four-digit year, `.pdf` extension:

| Good | Avoid |
|------|--------|
| `Citizen_Kane_1941.pdf` | `kane.pdf`, `Citizen Kane (1941).pdf` |

```bash
# Staging-only (short action excerpts, no dialogue)
python3 scripts/import_uploaded_pdfs.py --studio welles

# Full screenplay text for training (dialogue kept → Title_full.txt)
python3 scripts/import_uploaded_pdfs.py --studio welles --full-screenplay
```

## Legal — uploading to GitHub

Feature screenplays are **copyrighted**. Putting full PDFs in a **public** GitHub repo is **redistribution** unless you have explicit rights. Prefer **local-only** copies or a private repo when unsure.

Study links (metadata only, no auto-download): `data/ingest/welles_script_slug_index.json` and `data/ingest/script_sources.md`.

## After upload

**Full screenplay path (recommended if you want dialogue in the LoRA):**

```bash
python3 scripts/import_uploaded_pdfs.py --studio welles --full-screenplay
python3 scripts/ingest_scripts.py --dataset manual --filter welles \
  --screenplay-mode full --max-pairs 0 --boost-titles "citizen kane" --boost-repeat 3
```

Outputs land in `data/scripts/welles/*_full.txt` and gitignored `data/ingest/script_pairs.jsonl` (one training row per scene chunk).