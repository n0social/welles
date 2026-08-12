# Style samples (high value for voice)

Drop `.txt` / `.md` excerpts here. `scripts/prepare_data.py` chunks them into SFT rows.

Included: `welles_register.md` — original Welles-tone pastiche (camera, mic, silence, city).

Tips:
- Prefer the voice you want: oratorical, cinematic, concrete first
- A few strong pages beat a pile of generic prose
- Optional private manuscripts at the repo root are no longer auto-ingested by the v2 prep mix (gold + style + light LongWriter)

Rebuild gold anytime:

```bash
python scripts/build_welles_gold.py
python scripts/prepare_data.py --max-examples 150 --gold-repeat 3
```
