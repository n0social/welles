# Welles

**Welles** is a LoRA adapter on [`Qwen/Qwen3-8B`](https://huggingface.co/Qwen/Qwen3-8B) fine-tuned to write in the **tone of Orson Welles** — oratorical, cinematic, and deliberate.

Not a chatbot. A writer.

- **Model:** [`n0social/welles`](https://huggingface.co/n0social/welles)
- **Desk UI:** [`welles.vercel.app`](https://welles.vercel.app) (`web/`)

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

| Path | Purpose |
|---|---|
| `hub/` | Model card / Hub README source |
| `web/` | Next.js writing desk (Vercel) |
| `notebooks/welles_colab.ipynb` | Train the adapter (Colab T4) |
| `notebooks/welles_serve.ipynb` | Serve inference (Colab + ngrok) |
| `space/modal_app.py` | Optional always-on Modal GPU API |
| `prompts/` | System / style prompt notes |
| `data/` | Training data prep inputs |

The published weights are a **PEFT / LoRA adapter**, not a full merged model. Load `Qwen/Qwen3-8B`, then apply `n0social/welles`.

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

## Desk + inference

```
Browser → Vercel (web/) → Colab ngrok or Modal → n0social/welles + Qwen3-8B
```

1. Run `notebooks/welles_serve.ipynb` on a Colab **T4** (keep the tab open) and copy the ngrok URL  
2. Open [welles.vercel.app](https://welles.vercel.app) → Settings → paste the API URL  
3. Write / Rewrite from the desk  

HF Gradio GPU Spaces need a paid plan. Modal is optional for a URL that stays up without a browser tab — see `web/README.md`.

## Training (v2 recipe)

| Item | Value |
|---|---|
| Base | `Qwen/Qwen3-8B` (Apache 2.0) |
| Method | QLoRA (4-bit NF4) + LoRA |
| LoRA | `r=16`, `alpha=32`, dropout `0.05` |
| Hardware | Google Colab Tesla T4 (16 GB) |
| Sequence length | 1024 |
| Epochs | 3 |
| Data mix | `data/welles_gold.jsonl` (×3) + style samples + capped LongWriter |

```bash
python scripts/build_welles_gold.py
python scripts/prepare_data.py --max-examples 150 --gold-repeat 3
```

Train from `notebooks/welles_colab.ipynb`. Eval before Hub push: `data/eval_checklist.md`.

## Training (v1 — shipped)

| Item | Value |
|---|---|
| LoRA | `r=8`, `alpha=16` |
| Epochs | 1 (~58 steps) |
| Data | LongWriter-heavy + thin gold |

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
- Free Colab serving needs an open notebook + fresh ngrok URL each session

## License

Adapter weights: **Apache 2.0**, same family as `Qwen/Qwen3-8B`.  
“Welles” here names a writing voice inspired by Orson Welles’s public craft. It is not affiliated with or endorsed by his estate.

## Links

- Model: https://huggingface.co/n0social/welles
- Base: https://huggingface.co/Qwen/Qwen3-8B
- Desk: https://welles.vercel.app
