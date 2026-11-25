# External screenplay datasets (local only)

Large third-party dumps live here after `scripts/fetch_external_datasets.py`. **Not committed to git** (see `.gitignore`). Re-run the script on Colab or your machine.

## Sources

| Directory | Origin | License (dataset) | Notes |
|-----------|--------|-------------------|--------|
| `inkwell-screenplay-revision-evaluation/` | [Inkwell-Software/screenplay-revision-evaluation](https://huggingface.co/datasets/Inkwell-Software/screenplay-revision-evaluation) | CC0-1.0 | 48 revision **eval** tasks; no gold rewrites |
| `atum09-screenplay-dataset/` | [Atum09/screenplay-dataset](https://huggingface.co/datasets/Atum09/screenplay-dataset) | See Hub `LICENSE` | Synthetic SFT; includes `script_coverage`, `rewrite_punchup` |
| `kaggle-movie-scripts-corpus/` | [gufukuro/movie-scripts-corpus](https://www.kaggle.com/datasets/gufukuro/movie-scripts-corpus) | CC BY-NC-SA 4.0 | ~2.2 GB; **non-commercial**; screenplay text is still copyrighted |

**Movie Scripts Corpus** can also be fetched from Harvard Dataverse (same Kaggle snapshot):

- DOI [10.7910/DVN/PZTL2L](https://doi.org/10.7910/DVN/PZTL2L) — `MovieScriptsCorpus.zip` (~660 MB)

Use `--dataverse-movie-corpus` when Kaggle CLI credentials are unavailable.

## Fetch

```bash
pip install huggingface_hub kaggle   # kaggle optional
python3 scripts/fetch_external_datasets.py --hf inkwell,atum09
python3 scripts/fetch_external_datasets.py --kaggle-movie-corpus   # needs ~/.kaggle/kaggle.json
python3 scripts/fetch_external_datasets.py --dataverse-movie-corpus
python3 scripts/fetch_external_datasets.py --all   # HF + best-effort movie corpus
```

After download, see `MANIFEST.json` for byte sizes.

## Welles use

- **Inkwell:** regression tests for constrained revision (`scripts/convert_external_datasets.py --inkwell-eval`).
- **Atum09:** filter categories then map to Welles messages (`--atum09-coverage` sample export).
- **Movie corpus:** metadata joins (Welles writer/director), optional offline excerpt policy — do not republish full scripts in a public Hub dataset.

Convert helpers write small **samples** under `data/ingest/external_samples/` (safe to inspect; gitignored unless you opt in).