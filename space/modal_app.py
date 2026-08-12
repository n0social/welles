"""Welles GPU inference on Modal (replaces paid HF Gradio Space).

Deploy:
  pip install modal
  modal setup
  modal deploy space/modal_app.py

Then set on Vercel:
  WELLES_API_URL=https://<your-modal-username>--welles-generate.modal.run
"""

from __future__ import annotations

import modal

APP_NAME = "welles"
IMAGE = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "peft",
        "safetensors",
        "sentencepiece",
        "protobuf",
        "fastapi",
        "huggingface_hub",
    )
    .env({"HF_HOME": "/root/.cache/huggingface"})
)

app = modal.App(APP_NAME)
volume = modal.Volume.from_name("welles-hf-cache", create_if_missing=True)

ADAPTER_ID = "n0social/welles"
BASE_ID = "Qwen/Qwen3-8B"
SYSTEM = (
    "You are Welles, a writer in the voice of Orson Welles: "
    "oratorical, cinematic, and deliberate."
)
MODES = {
    "Write": "Write the following in your voice.",
    "Rewrite": "Rewrite the following in your voice. Keep the substance.",
    "Continue": "Continue from the following in your voice. Hold one argument to the end.",
}


def _load():
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_ID)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_ID,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(model, ADAPTER_ID)
    model.eval()
    return tokenizer, model


@app.cls(
    image=IMAGE,
    gpu="T4",
    timeout=600,
    scaledown_window=120,
    volumes={"/root/.cache/huggingface": volume},
)
class Welles:
    @modal.enter()
    def setup(self):
        self.tokenizer, self.model = _load()

    @modal.method()
    def generate(self, mode: str, prompt: str, max_new_tokens: int = 768) -> str:
        import torch

        text = (prompt or "").strip()
        if not text:
            return "Enter a brief or draft first."
        if mode not in MODES:
            mode = "Write"

        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"{MODES[mode]}\n\n{text}"},
        ]
        rendered = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self.tokenizer(rendered, return_tensors="pt").to(self.model.device)
        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=int(max_new_tokens),
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        new_tokens = out[0][inputs["input_ids"].shape[-1] :]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


@app.function(image=IMAGE, timeout=600)
@modal.fastapi_endpoint(method="POST")
def generate(body: dict):
    """HTTP entry for Vercel: POST JSON {mode, prompt, maxNewTokens}."""
    mode = (body or {}).get("mode") or "Write"
    prompt = (body or {}).get("prompt") or ""
    max_new_tokens = int(
        (body or {}).get("maxNewTokens")
        or (body or {}).get("max_new_tokens")
        or 768
    )
    max_new_tokens = max(256, min(2048, max_new_tokens))
    text = Welles().generate.remote(mode, prompt, max_new_tokens)
    return {"text": text}
