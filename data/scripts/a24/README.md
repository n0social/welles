# Manual A24-adjacent script drops

Place **`.txt`** or **`.md`** staging excerpts here for:

```bash
python3 scripts/ingest_scripts.py --dataset manual --filter a24
```

There is **no official A24 screenplay dataset** on Hugging Face. Default HF path filters **A24-likely titles inside MovieSum** (stage directions only). Use this folder for material you have rights to (original exercises, licensed sides, permitted workshop drafts).

### PDF → txt workflow (Script Slug / Cole Haddon / award PDFs)

1. Titles: [`data/ingest/a24_titles.json`](../../ingest/a24_titles.json) (`scripts/scrape_a24_metadata.py`).
2. Drop PDFs in [`incoming/`](incoming/) (gitignored).
3. `python3 scripts/extract_screenplay_pdf.py` → `*_excerpt.txt` here (staging-only chunks).
4. Or manual `pdftotext`; then `ingest_scripts.py --dataset manual --filter a24`.

See [`data/ingest/script_sources.md`](../../ingest/script_sources.md) for Script Slug / Cole Haddon legal notes.