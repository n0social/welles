# Incoming A24 screenplay PDFs (local only)

Drop **PDFs you downloaded yourself** (Script Slug, Cole Haddon links, award PDFs, etc.).

```bash
# Staging excerpts → data/scripts/a24/*_excerpt.txt (git: keep short)
python3 scripts/extract_screenplay_pdf.py

python3 scripts/ingest_scripts.py --dataset manual --filter a24
```

- `*.pdf` here is **gitignored** — do not commit copyrighted full scripts.
- Repo **does not** auto-download from scriptslug.com (see ToS §9 in `data/ingest/script_sources.md`).