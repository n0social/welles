"""Welles inference Space — GPU API for the Vercel UI.

Deploy as Hugging Face Space (Gradio + ZeroGPU).
The Next.js app calls api_name=\"generate\".
"""

from __future__ import annotations

import gradio as gr
import spaces
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

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

tokenizer = AutoTokenizer.from_pretrained(ADAPTER_ID)
model = AutoModelForCausalLM.from_pretrained(
    BASE_ID,
    torch_dtype=torch.float16,
    device_map="auto",
)
model = PeftModel.from_pretrained(model, ADAPTER_ID)
model.eval()


@spaces.GPU(duration=120)
def generate(mode: str, prompt: str, max_new_tokens: float) -> str:
    text = (prompt or "").strip()
    if not text:
        return "Enter a brief or draft first."
    if mode not in MODES:
        mode = "Write"

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{MODES[mode]}\n\n{text}"},
    ]
    rendered = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = tokenizer(rendered, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        out = model.generate(
            **inputs,
            max_new_tokens=int(max_new_tokens),
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


with gr.Blocks(title="Welles API") as demo:
    gr.Markdown(
        "# Welles API\n"
        "Inference backend for the Vercel UI. "
        "Call `generate` via the Gradio client (`n0social/welles` Space)."
    )
    mode = gr.Radio(["Write", "Rewrite", "Continue"], value="Write", label="Mode")
    prompt = gr.Textbox(lines=12, label="Brief or draft")
    max_tokens = gr.Slider(256, 2048, value=768, step=128, label="Max new tokens")
    out = gr.Textbox(lines=16, label="Welles")
    btn = gr.Button("Generate", variant="primary")
    btn.click(
        generate,
        inputs=[mode, prompt, max_tokens],
        outputs=[out],
        api_name="generate",
    )

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1).launch()
