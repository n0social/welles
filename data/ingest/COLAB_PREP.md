# Colab prep — validate data before GPU

## 1. Build on Colab (after `git pull` + `git lfs pull`)

```bash
!pip install -q pypdf datasets peft trl transformers bitsandbytes accelerate
!python scripts/build_script_corpus.py
!python scripts/review_training_data.py
```

Open `data/ingest/corpus_review.md` and skim **random samples** + **Kane** samples.

## 2. Does this mix match your goals?

| Signal | What you should see |
|--------|---------------------|
| **verbatim** | Full scenes: sluglines, action, dialogue (Kane Xanadu opening is a good sanity check). |
| **continue / bridge** | Mid-scene and scene-to-scene continuation. |
| **compose** | Staging spine → fuller scene text. |
| **structure** | Short beat-analysis blurbs (~70w), not full screenplay. |
| **welles gold** | ~276 rows in default mix — small vs 16k scripts. |

## 3. Tone-first v1 mix (recommended before first train)

Screenplay rows dominate by default. To keep **initial Welles desk voice** while learning script craft:

```bash
python3 scripts/prepare_data.py \
  --fetch-scripts --scripts-cache data/ingest/script_pairs.jsonl \
  --max-scripts 4000 \
  --gold-repeat 5 \
  --max-cinema 30 --max-examples 50
```

Or use full script corpus but train **two epochs** and eval desk prompts before Hub push.

## 4. Train

`notebooks/welles_colab.ipynb` or:

```bash
python3 scripts/train.py
```

Checklist: `data/eval_checklist.md` (desk voice) **and** spot-read Kane scene generation.

## 5. Red flags (do not train yet)

- No Kane rows in `script_pairs` (re-run extract on `Citizen-Kane-Script.pdf`).
- Almost all completions &lt; 20 words.
- `train.jsonl` missing `WRITE.` / `REWRITE.` gold rows entirely.