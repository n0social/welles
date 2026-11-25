#!/usr/bin/env bash
# One-shot Colab / GPU VM: local PDFs + external HF + merged train.jsonl
set -euo pipefail
cd "$(dirname "$0")/.."

pip install -q pypdf huggingface_hub datasets peft trl transformers bitsandbytes accelerate

echo "=== 1. External datasets (local cache under data/external/) ==="
python3 scripts/fetch_external_datasets.py --hf inkwell,atum09
python3 scripts/fetch_external_datasets.py --dataverse-movie-corpus || \
  python3 scripts/fetch_external_datasets.py --kaggle-movie-corpus || true

echo "=== 2. Welles PDF corpus → script_pairs.jsonl ==="
git lfs pull 2>/dev/null || true
python3 scripts/build_script_corpus.py --build-train --skip-extract 2>/dev/null || \
  python3 scripts/build_script_corpus.py --build-train

echo "=== 3. Merge gold + cinema + scripts + Atum09 → data/train.jsonl ==="
python3 scripts/prepare_data.py \
  --fetch-scripts \
  --scripts-cache data/ingest/script_pairs.jsonl \
  --max-scripts 0 \
  --gold-repeat 4 \
  --max-cinema 40 \
  --max-examples 80 \
  --max-external-atum09 1500

python3 scripts/review_training_data.py
echo "Done. Train with: python3 scripts/train.py  or notebooks/welles_colab.ipynb"