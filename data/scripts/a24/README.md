# Manual A24-adjacent script drops

Place **`.txt`** or **`.md`** staging excerpts here for:

```bash
python3 scripts/ingest_scripts.py --dataset manual --filter a24
```

There is **no official A24 screenplay dataset** on Hugging Face. Default HF path filters **A24-likely titles inside MovieSum** (stage directions only). Use this folder for material you have rights to (original exercises, licensed sides, permitted workshop drafts).

### PDF → txt workflow (Script Slug / Cole Haddon / award PDFs)

1. Use [`data/ingest/a24_titles.csv`](../../ingest/a24_titles.csv) or Script Slug’s [A24 index](https://www.scriptslug.com/scripts/studio/a24) to pick a title.
2. Download PDF **on your machine** (never via repo scrapers).
3. Convert: `pdftotext screenplay.pdf moonlight_2016.txt` (name files `title_year.txt` when possible).
4. Prefer **short staging excerpts** if anything might land in git; full texts stay local → `script_pairs.jsonl` only.

See [`data/ingest/script_sources.md`](../../ingest/script_sources.md) for Script Slug / Cole Haddon legal notes.