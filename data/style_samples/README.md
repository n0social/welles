# Style samples (high value for voice)

Drop `.txt` / `.md` excerpts here. `scripts/prepare_data.py` chunks them into SFT rows.

Included: `welles_register.md` — original Welles-tone pastiche (camera, mic, silence, city).

Tips:
- Prefer the voice you want: oratorical, cinematic, concrete first
- A few strong pages beat a pile of generic prose
- **Cinema ingest** (`data/ingest/`, `scripts/ingest_cinema.py`) adds HF wiki plots and MovieSum summaries as a capped tier in `prepare_data.py` (`--max-cinema 60` default). Run ingest first, or use `--fetch-cinema` on a machine with Hub access. Voice still comes from gold + this folder.
- Optional private manuscripts at the repo root are no longer auto-ingested by the v2 prep mix (gold + style + cinema + light LongWriter)

Rebuild gold anytime:

```bash
python scripts/build_welles_gold.py
python scripts/ingest_cinema.py --max-wiki 400 --max-moviesum 40
python scripts/prepare_data.py --max-examples 150 --gold-repeat 3 --max-cinema 60
```
