"""QLoRA SFT for Welles on Qwen3-8B. Cloud GPU only (e.g. RunPod / Colab T4)."""

from __future__ import annotations

from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "train.jsonl"
OUT = ROOT / "outputs" / "welles"

BASE_MODEL = "Qwen/Qwen3-8B"
HUB_ID = "n0social/welles"


def disable_transformers_allocator_warmup() -> None:
    """Colab T4: transformers pre-alloc can OOM before weights load."""
    try:
        import transformers.modeling_utils as modeling_utils

        modeling_utils.caching_allocator_warmup = lambda *args, **kwargs: None  # noqa: ARG005
    except Exception:
        pass


def patch_trl_chunked_logprob_for_sm75() -> None:
    """TRL assistant_only_loss on torch>=2.8 uses bf16→fp32 addmm; T4 (sm<80) cannot."""
    try:
        import trl.kernels.chunked_logprob as chunked_logprob

        chunked_logprob._MM_OUT_DTYPE = False
    except Exception:
        pass


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}. Run: python scripts/prepare_data.py")

    dataset = load_dataset("json", data_files=str(DATA), split="train")

    # Colab T4 = sm_75 — no bf16 GEMM; tight 16 GB VRAM.
    # T4: keep both fp16/bf16 off in the trainer — fp16 GradScaler + stray bf16 grads from
    # 4-bit Qwen blows up on recent Colab torch ("_amp_foreach... not implemented for BFloat16").
    cap = torch.cuda.get_device_capability()[0] if torch.cuda.is_available() else 0
    use_bf16 = cap >= 8
    compute_dtype = torch.bfloat16 if use_bf16 else torch.float16
    max_length = 1024 if cap < 8 else 2048

    if cap < 8:
        disable_transformers_allocator_warmup()
        patch_trl_chunked_logprob_for_sm75()

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )
    load_kwargs: dict = {
        "quantization_config": quant_config,
        "device_map": {"": 0},
        "attn_implementation": "sdpa",
    }
    if cap < 8:
        # T4: skip torch_dtype on load (4-bit only); avoid prepare_model_for_kbit_training fp32 norm cast (OOM).
        load_kwargs["max_memory"] = {0: "13GiB"}

    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, **load_kwargs)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    lora_r = 8 if cap < 8 else 16
    trainer = SFTTrainer(
        model=model,
        args=SFTConfig(
            output_dir=str(OUT),
            learning_rate=2e-4,
            num_train_epochs=2 if cap < 8 else 3,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=16 if cap < 8 else 8,
            gradient_checkpointing=True,
            max_length=max_length,
            logging_steps=10,
            save_steps=100,
            fp16=False,
            bf16=use_bf16,
            assistant_only_loss=True,
            report_to="none",
        ),
        train_dataset=dataset,
        peft_config=LoraConfig(
            r=lora_r,
            lora_alpha=32,
            lora_dropout=0.05,
            task_type="CAUSAL_LM",
            bias="none",
        ),
    )

    trainer.train()
    trainer.save_model(str(OUT / "adapter"))
    print(f"Saved adapter to {OUT / 'adapter'}")
    print(f"When ready: trainer.push_to_hub('{HUB_ID}')")


if __name__ == "__main__":
    main()
