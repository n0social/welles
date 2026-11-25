"""QLoRA SFT for Welles on Qwen3-8B. Cloud GPU only (e.g. RunPod / Colab T4)."""

from __future__ import annotations

from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "train.jsonl"
OUT = ROOT / "outputs" / "welles"

BASE_MODEL = "Qwen/Qwen3-8B"
HUB_ID = "n0social/welles"


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}. Run: python scripts/prepare_data.py")

    dataset = load_dataset("json", data_files=str(DATA), split="train")

    # Colab T4 = sm_75 — bf16 GEMM in trl fails; A100+ can use bf16.
    use_bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8
    compute_dtype = torch.bfloat16 if use_bf16 else torch.float16

    trainer = SFTTrainer(
        model=BASE_MODEL,
        args=SFTConfig(
            output_dir=str(OUT),
            learning_rate=2e-4,
            num_train_epochs=3,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            gradient_checkpointing=True,
            max_length=2048,  # full screenplay scene chunks (~380 words); use 1024 for staging-only mixes
            logging_steps=10,
            save_steps=100,
            fp16=not use_bf16,
            bf16=use_bf16,
            assistant_only_loss=True,
            model_init_kwargs={
                "torch_dtype": compute_dtype,
                "device_map": {"": 0},
            },
        ),
        train_dataset=dataset,
        peft_config=LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            task_type="CAUSAL_LM",
        ),
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
        ),
    )

    trainer.train()
    trainer.save_model(str(OUT / "adapter"))
    print(f"Saved adapter to {OUT / 'adapter'}")
    print(f"When ready: trainer.push_to_hub('{HUB_ID}')")


if __name__ == "__main__":
    main()
