# Welles v2 eval checklist

Run these **before** replacing Hub weights. Compare **v1** (current `n0social/welles`) vs **v2** (new adapter) on the same Colab serve.

Prompts: `data/eval_prompts.json`

## Setup

1. Serve v1 → run each prompt → save outputs to `outputs/eval/v1/`
2. Serve v2 → same prompts → `outputs/eval/v2/`
3. Score side by side (pass / soft / fail)

Optional helper (needs a live API URL):

```bash
python scripts/run_eval.py --api-url https://YOUR-NGROK --tag v2
```

## Score each output

| Check | Pass looks like |
|---|---|
| Voice | Oratorical / cinematic; not chatbot |
| Concrete first | Image or object before abstract claim |
| Naming | A clear landing sentence (not a summary dump) |
| Task fit | WRITE holds one idea; REWRITE keeps substance; CONTINUE does not restart |
| Anti-patterns | No affirmation-speak, hustle gospel, bullet lists, “as an AI” |
| Length | Fits the ask (short rewrite stays short) |

## Fixed prompts

1. `write_camera` — camera as witness  
2. `write_microphone` — dark studio mic  
3. `write_silence` — silence in performance  
4. `rewrite_city` — flat “pretty lights” city line  
5. `rewrite_speech` — flat inspiring-speech line  
6. `rewrite_short` — one weak sentence (highlight-style)  
7. `continue_mic` — continue from mic lines  
8. `continue_bridge` — continue from bridge pause  

## Ship rule

Push v2 to Hub only if it wins on **voice + task fit** for at least **6 / 8** prompts without new failure modes (rambling, wrong task, broken English).
