# Welles — the Architect

An AI that **reworks, writes, and completes** the Working Bee trilogy. You bring drafts and gaps. The architect writes the pages.

1. *The Working Bee* — heat (extraction)
2. *The Unpaid Hour* — cooling (one hour taken back)
3. *The Craftsmen* — making (passion/hobby; no draft yet)

Base: `Qwen/Qwen3-8B` → `n0social/welles`. Train on a **cloud GPU**, not the laptop or the droplet.

## What the architect does

| Job | You give | It returns |
|---|---|---|
| Rework | Paper-like chapter | Hymn + fact with basis |
| Write | Book + title/brief | New chapter or psalm |
| Complete | Inconclusive draft | A close, no backtrack |

Spec: `prompts/welles_system.md`, `prompts/hymns.md`, `prompts/series.md`.

## Data

- Your manuscripts (Bee, Hour)
- Gold architect tasks: `data/architect_gold.jsonl`
- Tone spine: `data/companion/` (Veblen, Ruskin, Carlyle, George, London, Riis)
- Length: LongWriter-6k

```bash
pip install datasets
python scripts/prepare_data.py
```

## Train (Google Colab)

Beginner path: open `notebooks/welles_colab.ipynb` in [Google Colab](https://colab.research.google.com/). Use a **T4 GPU**. Zip this folder (without the token file), upload, run the cells in order.

Push adapter to `n0social/welles`.

**UI:** Next.js on Vercel (`web/`) → GPU API on **Colab** (`notebooks/welles_serve.ipynb`) or **Modal** (`space/modal_app.py`) → Hub adapter `n0social/welles`.  
HF Gradio Spaces need a paid GPU plan. See `web/README.md`.
