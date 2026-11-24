# Incoming A24 screenplay PDFs

Upload **PDFs you obtained yourself** (Script Slug browser save, Cole Haddon links, award PDFs, etc.) to this folder, then run the extract + ingest pipeline.

## Naming

Use **`Title_Year.pdf`** — underscores, four-digit year, `.pdf` extension:

| Good | Avoid |
|------|--------|
| `Moonlight_2016.pdf` | `moonlight.pdf`, `Moonlight (2016).pdf` |
| `moonlight-2016.pdf` (kebab + year) | random names without a year |

If PDFs were uploaded to the repo-root `scripts/` folder by mistake, run `python3 scripts/import_uploaded_pdfs.py` once — it moves them here automatically.

Run `python3 scripts/import_uploaded_pdfs.py` to validate names and PDF headers before extract.

## Legal — uploading to GitHub

Feature screenplays are **copyrighted**. Putting full PDFs in a **public** GitHub repo is **redistribution** of those works unless you have explicit rights.

| Setup | Risk |
|--------|------|
| **Public repo** + committed PDFs | High — treat as publishing studio scripts |
| **Private repo** + committed PDFs | Lower visibility; still not a training/redistribution license |
| PDFs **local only** (never `git add`) | Lowest — recommended if you are unsure |

This project **allows** committing PDFs under `incoming/*.pdf` when **you** accept that risk (see root `.gitignore` comment). Prefer a **private fork** or keep PDFs off GitHub. PDFs can be **large** (often 1–5 MB each); consider [Git LFS](https://git-lfs.com/) (see repo `.gitattributes`).

There is **no** automated Script Slug bulk download in this repo. Optional one-at-a-time helper: `scripts/download_screenplay_pdf.py` (see `data/ingest/script_sources.md`).

## After upload — three commands

```bash
# 1) Verify incoming PDFs + batch extract → data/scripts/a24/*_excerpt.txt
python3 scripts/import_uploaded_pdfs.py

# Or call extract directly:
# python3 scripts/extract_screenplay_pdf.py

# 2) Staging excerpts live in data/scripts/a24/ (dialogue-stripped chunks)

# 3) Merge into local script_pairs.jsonl (gitignored)
python3 scripts/ingest_scripts.py --dataset manual --filter a24
```

`extract_screenplay_pdf.py` caps excerpt size; it does not commit full script text to tracked training files.