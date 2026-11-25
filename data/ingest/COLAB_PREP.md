# Colab prep — validate data before GPU

## 0. Git LFS (required for PDF scripts on Colab)

`git clone` alone leaves **pointer files**, not PDFs (`missing %PDF header`, `b'versi'` errors).

Run **before** `build_script_corpus.py`:

```bash
apt-get install -y git-lfs
git lfs install
cd /content/welles   # your repo root
git lfs pull
head -c 8 data/scripts/welles/incoming/Citizen-Kane-Script.pdf
```

You must see `%PDF-1.` at the start. If you see `version`, LFS did not pull.

## 1. Combined training mix (ours + external)

**Ours:** Welles/A24 PDFs → `script_pairs.jsonl`, gold, style, cinema.  
**External:** Inkwell (eval), Atum09 coverage/punch-up (train), Movie Scripts Corpus (optional offline pool in `data/external/`).

One-shot:

```bash
bash scripts/build_colab_training.sh
```

Or step by step:

```bash
pip install -q pypdf huggingface_hub datasets peft trl transformers bitsandbytes accelerate
python3 scripts/fetch_external_datasets.py --hf inkwell,atum09
python3 scripts/fetch_external_datasets.py --dataverse-movie-corpus   # or --kaggle-movie-corpus
python3 scripts/build_script_corpus.py --build-train
python3 scripts/prepare_data.py \
  --fetch-scripts --scripts-cache data/ingest/script_pairs.jsonl \
  --max-scripts 0 --gold-repeat 4 --max-cinema 40 --max-examples 80 \
  --max-external-atum09 1500
python3 scripts/review_training_data.py
```

`--max-external-atum09` pulls from `data/external/atum09-screenplay-dataset/` (or `external_samples/` fallback). Atum09 `thinking` text is wrapped in Qwen think tags when present — useful if you later train with `enable_thinking=True`.

**Inkwell** stays **eval** only (`data/ingest/external_samples/inkwell_revision_eval.jsonl`), not merged into `train.jsonl`.

## 2. Build on Colab (after `git pull` + `git lfs pull`)

```bash
!pip install -q pypdf datasets peft trl transformers bitsandbytes accelerate
!python scripts/build_script_corpus.py
!python scripts/review_training_data.py
```

Open `data/ingest/corpus_review.md` and skim **random samples** + **Kane** samples.

## 3. Does this mix match your goals?

| Signal | What you should see |
|--------|---------------------|
| **verbatim** | Full scenes: sluglines, action, dialogue (Kane Xanadu opening is a good sanity check). |
| **continue / bridge** | Mid-scene and scene-to-scene continuation. |
| **compose** | Staging spine → fuller scene text. |
| **structure** | Short beat-analysis blurbs (~70w), not full screenplay. |
| **welles gold** | ~276 rows in default mix — small vs 16k scripts. |

## 4. Tone-first v1 mix (recommended before first train)

Screenplay rows dominate by default. To keep **initial Welles desk voice** while learning script craft:

```bash
python3 scripts/prepare_data.py \
  --fetch-scripts --scripts-cache data/ingest/script_pairs.jsonl \
  --max-scripts 4000 \
  --gold-repeat 5 \
  --max-cinema 30 --max-examples 50
```

Or use full script corpus but train **two epochs** and eval desk prompts before Hub push.

## 5. Train

`notebooks/welles_colab.ipynb` or:

```bash
python3 scripts/train.py
```

**T4 / Colab:**

- `SFTConfig`: `fp16=False`, `bf16=False` (LoRA-only updates; `fp16=True` can break GradScaler on bf16 grads).
- **Before** `SFTTrainer` / `trainer.train()`: TRL `assistant_only_loss` needs a sm&lt;80 patch on PyTorch 2.8+:

```python
import trl.kernels.chunked_logprob as _cl
_cl._MM_OUT_DTYPE = False
```

Without this: `gemm input type at::BFloat16 and output type float is only supported for CUDA ... 8.0 or higher`.

`python3 scripts/train.py` applies both patches on T4 automatically.

After a failed train, **Runtime → Restart session** and train in a clean kernel (do not load the 8B model twice).

Checklist: `data/eval_checklist.md` (desk voice) **and** spot-read Kane scene generation.

## 6. Red flags (do not train yet)

- No Kane rows in `script_pairs` (re-run extract on `Citizen-Kane-Script.pdf`).
- Almost all completions &lt; 20 words.
- `train.jsonl` missing `WRITE.` / `REWRITE.` gold rows entirely.