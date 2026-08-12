# Writer AI — Build Findings

**Date:** 2026-08-11  
**Workspace:** `Writer_ai` (empty at time of research)  
**Goal:** Fine-tune a custom text-generation model, host the weights on Hugging Face Hub, and ship a public Gradio demo on Hugging Face Spaces.

### Decisions recorded

| Item | Choice |
|---|---|
| Product name | **Welles** (the Architect: rework / write / complete the trilogy) |
| Hugging Face username | `n0social` |
| Model repo (planned) | `n0social/welles` |
| Space (planned) | `n0social/welles` |
| Training hardware | Cloud GPU preferred (RunPod / Colab). P3200 (~6 GB) is fallback / local GGUF inference only. |
| Serving architecture | Weights + GPU inference on Hugging Face. DigitalOcean droplet hosts a thin web frontend only. |
| Dataset (v1) | `zai-org/LongWriter-6k` (subset / length-capped for first run) |
| Base model (recommended) | **`Qwen/Qwen3-8B`** (Apache 2.0, ungated, ~32k native output). Instruct-style; disable thinking for writing. |
| Genre / voice | Trilogy under one hive. (1) *The Working Bee* — extraction, stern manifesto. (2) *The Unpaid Hour* — wellness as reclaim/limit. (3) *The Craftsmen* — creation through passion and hobby, not hustle. |
| Completion problem | Drafts drift and backtrack. Welles must stay in-book and carry the through-line: hive takes the day → unpaid hour → making. |

This document captures the original three-step plan, what current Hugging Face docs actually require, and the decisions we still need before implementation.

---

## What we are building

Three independent artifacts:

| Artifact | Where it lives | Purpose |
|---|---|---|
| Training code + dataset | This repo (local / Colab / cloud GPU) | Adapt a base LLM to our writing task |
| Model repo | `https://huggingface.co/<user>/<model>` | Store weights, tokenizer, model card |
| Space (web app) | `https://huggingface.co/spaces/<user>/<space>` | Let anyone try the model in a browser |

The original plan is correct at a high level. Several APIs, hosting rules, and packaging details have changed and must be accounted for.

---

## Step 1 — Environment, data, and training

### Packages

Original install:

```bash
pip install torch transformers datasets accelerate peft trl huggingface_hub
```

**Add `bitsandbytes` if we use QLoRA** (4-bit quantization). It is not in the original list but is required for QLoRA.

Recommended install (Windows + NVIDIA GPU):

```bash
# Install PyTorch with CUDA from pytorch.org first, then:
pip install transformers datasets accelerate peft trl huggingface_hub bitsandbytes gradio
```

Notes:

- Install **CUDA-enabled PyTorch** from [pytorch.org](https://pytorch.org), not the default CPU wheel, if we train locally.
- `bitsandbytes` now supports Windows 11 + NVIDIA CUDA for QLoRA (v0.50+). Still verify `torch.cuda.is_available()` before training.
- CPU-only training of even a 1B–3B model is impractically slow. Use a local NVIDIA GPU, Google Colab, Kaggle, or a cloud GPU.
- `accelerate` is used under the hood by TRL / Transformers `Trainer`. We do not need a custom training loop.

### Dataset format

TRL’s `SFTTrainer` accepts **JSONL** (preferred) or anything `datasets` can load. Four official formats:

**1. Language modeling (raw completions)**

```json
{"text": "The sky is blue."}
```

**2. Conversational (best for a writing assistant)**

```json
{"messages": [
  {"role": "system", "content": "You are a helpful writing assistant."},
  {"role": "user", "content": "Rewrite this sentence more clearly: ..."},
  {"role": "assistant", "content": "..."}
]}
```

**3. Prompt–completion (instruction tuning)**

```json
{"prompt": "Rewrite this sentence more clearly: ...", "completion": "..."}
```

**4. Conversational prompt–completion**

```json
{"prompt": [{"role": "user", "content": "Rewrite this sentence more clearly: ..."}],
 "completion": [{"role": "assistant", "content": "..."}]}
```

Load a local JSONL file:

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="data/train.jsonl", split="train")
```

**Recommendation for Writer AI:** conversational `messages` JSONL with a system prompt that defines the writing style. Set `assistant_only_loss=True` in `SFTConfig` so the model is not penalized for predicting the user prompt.

Quality matters more than volume. A few hundred high-quality input/output pairs can beat thousands of noisy ones for a narrow writing task.

### Training: SFT + PEFT / QLoRA

Use **SFTTrainer** from `trl`, not a hand-rolled loop.

**LoRA (PEFT)** trains a small adapter on top of a frozen base model. Cheap, small upload, base weights stay on the Hub.

**QLoRA** = LoRA + 4-bit quantization. Lets a 7B model train on a consumer GPU (~8–16 GB VRAM).

Minimal QLoRA sketch (current TRL API):

```python
from datasets import load_dataset
from peft import LoraConfig
from transformers import BitsAndBytesConfig
from trl import SFTTrainer, SFTConfig

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="bfloat16",
)

trainer = SFTTrainer(
    model="Qwen/Qwen3-0.6B",  # placeholder — pick a real base later
    args=SFTConfig(
        output_dir="outputs",
        learning_rate=2e-4,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        assistant_only_loss=True,
        packing=True,
    ),
    train_dataset=load_dataset("json", data_files="data/train.jsonl", split="train"),
    peft_config=peft_config,
    quantization_config=bnb_config,
)
trainer.train()
trainer.save_model("outputs/adapter")
```

**After training we must choose how to publish:**

| Option | What gets uploaded | Space impact |
|---|---|---|
| Adapter only (`PeftModel`) | Small (tens of MB) | Space must load **base model + adapter** |
| Merged full model (`merge_and_unload()`) | Full size of the base model | Simpler `pipeline("text-generation", model=...)` |

The original plan (`model.push_to_hub(...)`) assumes a **full merged model**. That is the simplest path for the Gradio snippet. Adapter-only is cheaper to store and iterate on.

### Base model (not specified in the original plan)

We still need to pick one. Practical starting points for a writing app:

| Model class | Size | Notes |
|---|---|---|
| Qwen3 / Qwen2.5 | 0.5B–7B | Strong small models; easy SFT; permissive licenses vary by size |
| Llama 3.x Instruct | 1B–8B | Gated on Hub — Space needs `HF_TOKEN` |
| Gemma 2 / 3 | 2B–9B | Google license; gated |
| SmolLM / Phi | <3B | Fits CPU/ZeroGPU more easily |

**Spaces reality:** a 7B+ full-precision model will not run on free CPU hardware. Prefer a **small instruct model (0.5B–3B)** or ship a **LoRA adapter** on a small base, unless we pay for GPU hardware.

---

## Step 2 — Host weights on Hugging Face Hub

Hugging Face Hub is a Git repo for models: weights, tokenizer, config, and a model card (`README.md`).

### Auth

Original command still works, but current docs prefer:

```bash
hf auth login
```

(`huggingface-cli login` is the older alias.)

Token: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — needs **Write** permission. Never commit the token.

### Push from Python

Original snippet is valid for a **full** `PreTrainedModel`:

```python
model.push_to_hub("your-username/my-custom-ai-model")
tokenizer.push_to_hub("your-username/my-custom-ai-model")
```

Better: let the trainer push so hyperparameters land on the model card:

```python
trainer.push_to_hub("your-username/writer-ai")
```

For a LoRA adapter:

```python
trainer.model.push_to_hub("your-username/writer-ai-lora")
tokenizer.push_to_hub("your-username/writer-ai-lora")
```

The adapter repo should declare `base_model` in the model card so the Hub (and Spaces) know which frozen weights to combine with.

### Model card (`README.md`)

A Hub model card is Markdown with **YAML front matter**. Minimum useful metadata:

```yaml
---
license: apache-2.0          # must be compatible with the base model license
base_model: Qwen/Qwen3-0.6B
tags:
  - text-generation
  - writing
  - sft
  - lora
language:
  - en
pipeline_tag: text-generation
datasets:
  - your-username/writer-ai-data
---

# Writer AI

## Intended use
Custom writing assistant fine-tuned for [task].

## Training
- Method: SFT + QLoRA
- Base: ...
- Data: ...

## Limitations
...
```

Edit in the Hub UI (**Edit model card**) or commit `README.md` with the weights.

---

## Step 3 — Gradio Space

### Create the Space

1. [https://huggingface.co/new-space](https://huggingface.co/new-space)
2. SDK: **Gradio** (required if we want free ZeroGPU)
3. Visibility: Public (or Private)
4. Hardware: see constraints below

Push `app.py` and `requirements.txt`. Every commit rebuilds the Space.

### Current hosting rules (important)

These differ from older tutorials that treat Spaces as fully free:

- **Static Spaces** are free.
- **Gradio / Docker Spaces** run on compute. Creating them generally requires **PRO** (personal) or Team/Enterprise (orgs).
- Exception: free personal accounts in good standing (verified email, account older than 30 days) can host **up to 2 ZeroGPU Gradio Spaces**.
- Default CPU Basic: 2 vCPU, 16 GB RAM, 50 GB ephemeral disk — **too weak for most LLMs**.
- **ZeroGPU** (Gradio-only): on-demand NVIDIA RTX Pro 6000 Blackwell, 48 GB (`large`) or 96 GB (`xlarge`). Visitors consume their own daily GPU quota (free ≈ 5 min, PRO ≈ 40 min).

**Implication:** for a custom LLM demo, plan on **ZeroGPU + Gradio**, not CPU Basic + a 7B model.

### Files

`requirements.txt` should pin enough to be reproducible, and include PEFT if we ship an adapter:

```
transformers
torch
accelerate
peft
gradio
spaces
```

`spaces` is required for the `@spaces.GPU` decorator on ZeroGPU.

### `app.py` — original vs production-ready

Original:

```python
import gradio as gr
from transformers import pipeline

pipe = pipeline("text-generation", model="your-username/my-custom-ai-model")

def generate_response(prompt):
    output = pipe(prompt, max_new_tokens=150)
    return output[0]["generated_text"]

demo = gr.Interface(fn=generate_response, inputs="text", outputs="text")
demo.launch()
```

Problems with that snippet for a writing app:

1. `generated_text` usually **includes the prompt**. Users will see their input echoed.
2. Instruct models expect a **chat template**, not a raw string. Use `pipe(messages)` or `tokenizer.apply_chat_template`.
3. Loading a large model at import time on ZeroGPU can fail or waste quota. Wrap inference with `@spaces.GPU`.
4. If the model is gated or private, set Space secret `HF_TOKEN`.
5. `max_new_tokens=150` is short for drafting; expose it as a slider.

More appropriate sketch:

```python
import gradio as gr
import spaces
from transformers import pipeline

MODEL_ID = "your-username/my-custom-ai-model"

pipe = pipeline(
    "text-generation",
    model=MODEL_ID,
    device_map="auto",
)

SYSTEM = "You are a helpful writing assistant."

@spaces.GPU
def generate_response(prompt, max_new_tokens=256):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt},
    ]
    out = pipe(messages, max_new_tokens=int(max_new_tokens), return_full_text=False)
    return out[0]["generated_text"]

demo = gr.Interface(
    fn=generate_response,
    inputs=[
        gr.Textbox(label="Prompt", lines=8),
        gr.Slider(32, 1024, value=256, step=32, label="Max new tokens"),
    ],
    outputs=gr.Textbox(label="Draft"),
    title="Writer AI",
)
demo.launch()
```

If we publish a **LoRA adapter**, load with:

```python
pipe = pipeline("text-generation", model="your-username/writer-ai-lora")
```

Transformers will pull the `base_model` listed on the adapter card, provided the Space can access that base (public or token).

Space README YAML should list the model so the Hub shows the link:

```yaml
---
title: Writer AI
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
suggested_hardware: zero-a10g
models:
  - your-username/my-custom-ai-model
---
```

---

## Gaps in the original tutorial

| Gap | Why it matters |
|---|---|
| No base model named | Size, license, VRAM, and chat template all depend on this |
| No dataset / writing task defined | “Writer AI” could mean rewrite, continue, style clone, or chat |
| `bitsandbytes` omitted | QLoRA will fail without it |
| Assumes full `push_to_hub` of a CausalLM | QLoRA actually saves adapters unless we merge |
| Spaces treated as always-free CPU | LLM demos need ZeroGPU or paid GPU |
| Raw `pipeline` on a string | Instruct models need chat templates |
| Echoed prompt in output | Bad UX |
| No eval split / quality checks | Easy to overfit a tiny custom set |
| License not discussed | Fine-tunes inherit base-model license constraints |
| Gated models | Llama/Gemma need Hub access + Space secret |

---

## Recommended repo layout (this workspace)

```
Writer_ai/
  FINDINGS.md                 # this file
  data/
    train.jsonl
    eval.jsonl
  scripts/
    train.py                  # SFTTrainer + optional QLoRA
    push.py                   # merge (optional) + push_to_hub
  space/
    app.py
    requirements.txt
    README.md                 # Space metadata
  requirements-train.txt
  README.md
```

Training stays in this Git repo. The Hub model repo and the Space repo are separate Hugging Face Git remotes (or we can add them as extra remotes later).

---

## Open decisions (block implementation)

1. **Task:** rewrite / continue / style-transfer / chat writing coach / something else?
2. **Base model** and license we can ship under.
3. **Where to train:** local Windows GPU, Colab, or rented cloud GPU?
4. **Publish format:** LoRA adapter vs merged full weights.
5. **Hugging Face username** and public vs private model/Space.
6. **Dataset:** existing files, scrape/export, or hand-authored examples?

---

## Sources

- [TRL SFT Trainer](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [TRL PEFT / QLoRA integration](https://huggingface.co/docs/trl/en/peft_integration)
- [Transformers fine-tuning](https://huggingface.co/docs/transformers/training)
- [Sharing models / `hf auth login`](https://huggingface.co/docs/transformers/en/model_sharing)
- [Model cards](https://huggingface.co/docs/hub/en/model-cards)
- [Spaces overview](https://huggingface.co/docs/hub/spaces-overview)
- [Gradio Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-gradio)
- [Spaces ZeroGPU](https://huggingface.co/docs/hub/en/spaces-zerogpu)
- [bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes)
- [freeCodeCamp: Get started with Hugging Face](https://www.freecodecamp.org/news/get-started-with-hugging-face/)
