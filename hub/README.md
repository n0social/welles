---
library_name: peft
base_model: Qwen/Qwen3-8B
tags:
  - qwen3
  - lora
  - qlora
  - text-generation
  - writing
  - orson-welles
  - sft
license: apache-2.0
language:
  - en
pipeline_tag: text-generation
---

# Welles

**Welles** is a LoRA adapter on [`Qwen/Qwen3-8B`](https://huggingface.co/Qwen/Qwen3-8B) fine-tuned to write in the **tone of Orson Welles** — oratorical, cinematic, and deliberate.

Not a chatbot. A writer.

## Highlights

- **Orson Welles register** — authority, cadence, and drama in the prose itself
- **Cinematic long-form** — essays, narration, and scripts that hold a frame and land a point
- **Rhetorical craft** — staged address, pause, and return; sentences with weight
- **Built for length** — trained to sustain argument across long passages, not one-liners
- **Drop-in LoRA** — sits on Qwen3-8B; small adapter, full base model underneath

## Voice

- Rhetorical and staged: address, pause, return to the object
- Concrete first — rooms, faces, light — then the naming sentence
- Length when the scene needs it; no empty flourish


## This repo

This is a **PEFT / LoRA adapter**, not a full merged model. Load `Qwen/Qwen3-8B`, then apply these weights.

| File | Purpose |
|---|---|
| `adapter_model.safetensors` | LoRA weights |
| `adapter_config.json` | PEFT config (base model, rank, targets) |
| Tokenizer files | Qwen3 chat template alignment |

## How to load

```python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_id = "Qwen/Qwen3-8B"
adapter_id = "n0social/welles"

tokenizer = AutoTokenizer.from_pretrained(adapter_id)
model = AutoModelForCausalLM.from_pretrained(
    base_id,
    torch_dtype=torch.float16,
    device_map="auto",
)
model = PeftModel.from_pretrained(model, adapter_id)

messages = [
    {
        "role": "system",
        "content": (
            "You are Welles, a writer in the voice of Orson Welles: "
            "oratorical, cinematic, and deliberate."
        ),
    },
    {
        "role": "user",
        "content": "Write a short essay on the camera as a witness.",
    },
]
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False,  # writing mode — disable Qwen3 thinking
)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=1024, do_sample=True, temperature=0.7)
print(tokenizer.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True))
```

## Training (v1)

| Item | Value |
|---|---|
| Base | `Qwen/Qwen3-8B` (Apache 2.0) |
| Method | QLoRA (4-bit NF4) + LoRA |
| LoRA | `r=8`, `alpha=16`, dropout `0.05` |
| Hardware | Google Colab Tesla T4 (16 GB) |
| Precision | float16 compute |
| Sequence length | 1024 |
| Epochs | 1 |
| Steps | 58 |
| Batch | 1 × 8 gradient accumulation |
| Optimizer | paged AdamW 8-bit |

Data: long-form English writing mixture (including a capped subset of [`zai-org/LongWriter-6k`](https://huggingface.co/datasets/zai-org/LongWriter-6k)) plus curated style material for a Welles-like register.

## Intended use

- Essays, narration, scripts, and long-form prose in a Welles-like register
- Rewrites that replace flat survey prose with staged, concrete argument

## Out of scope

- General customer-support chatbot
- Medical, legal, or financial advice
- Impersonation for fraud or deception

## Limitations

- v1 adapter — keep a strong system prompt; the base model still shows through
- Trained at 1024 tokens; longer pieces work best in sections
- Inspired by Welles’s public rhetorical style; not a verbatim clone of any one work
- Set `enable_thinking=False` (or equivalent) so Qwen3 stays in writing mode

## License

Adapter weights: **Apache 2.0**, same family as `Qwen/Qwen3-8B`.  
“Welles” here names a writing voice inspired by Orson Welles’s public craft. It is not affiliated with or endorsed by his estate.

## Citation

```bibtex
@misc{welles-lora-2026,
  title  = {Welles: Orson Welles–tone writing LoRA on Qwen3-8B},
  author = {n0social},
  year   = {2026},
  url    = {https://huggingface.co/n0social/welles}
}
```

## Links

- Model: https://huggingface.co/n0social/welles
- Base: https://huggingface.co/Qwen/Qwen3-8B
