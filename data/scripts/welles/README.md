# Manual Orson Welles script drops

Place **`.txt`** or **`.md`** files here for `scripts/ingest_scripts.py --dataset manual --filter welles`.

**PDF workflow:** upload `Title_Year.pdf` to [`incoming/`](incoming/README.md), then:

```bash
python3 scripts/import_uploaded_pdfs.py --studio welles
python3 scripts/ingest_scripts.py --dataset manual --filter welles
```

Title / study-link index (metadata only): `data/ingest/welles_script_slug_index.json`.

## What you may put here

- Staging-only excerpts you are entitled to use (no full copyrighted screenplay in git)
- Self-authored pastiche in screenplay layout
- Public-domain radio script fragments (verify per work)

## What not to commit

- Full IMSDb / studio PDF transcripts
- Scanned shooting scripts without clearance

Files in this folder are **not** gitignored; keep excerpts short. Prefer local-only full texts and let ingest chunk them into `data/ingest/script_pairs.jsonl` (ignored by git).

See [`data/ingest/script_sources.md`](../../ingest/script_sources.md) for filmography and legal notes.