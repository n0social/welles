"""Run fixed Welles eval prompts against a live generate API (Colab ngrok / Modal)."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "data" / "eval_prompts.json"


def generate(api_url: str, mode: str, prompt: str, max_new_tokens: int = 512) -> str:
    endpoint = api_url.rstrip("/")
    # Prefer /generate; many serves also accept POST /
    body = json.dumps(
        {
            "mode": mode.title() if mode.lower() != "continue" else "Continue",
            "prompt": prompt,
            "maxNewTokens": max_new_tokens,
            "max_new_tokens": max_new_tokens,
        }
    ).encode("utf-8")
    last_err: Exception | None = None
    for path in ("/generate", "/"):
        req = urllib.request.Request(
            endpoint + path if not endpoint.endswith(path) else endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return (data.get("text") or data.get("generation") or "").strip()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_err = exc
            continue
    raise RuntimeError(str(last_err) if last_err else "generate failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", required=True, help="Colab ngrok or Modal base URL")
    parser.add_argument("--tag", default="run", help="Label folder under outputs/eval/")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    args = parser.parse_args()

    items = json.loads(PROMPTS.read_text(encoding="utf-8"))
    out_dir = ROOT / "outputs" / "eval" / args.tag
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "tag": args.tag,
        "api_url": args.api_url,
        "started": datetime.now(timezone.utc).isoformat(),
        "results": [],
    }

    for item in items:
        pid = item["id"]
        mode = item.get("mode") or "WRITE"
        prompt = item["prompt"]
        print(f"→ {pid} ({mode})")
        try:
            text = generate(args.api_url, mode, prompt, args.max_new_tokens)
            err = None
        except Exception as exc:  # noqa: BLE001 — surface any transport/parse failure
            text = ""
            err = str(exc)
            print("  ERROR", err)

        (out_dir / f"{pid}.txt").write_text(text or f"[error] {err}", encoding="utf-8")
        manifest["results"].append(
            {"id": pid, "mode": mode, "error": err, "chars": len(text)}
        )

    manifest["finished"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out_dir}")
    print("Score with data/eval_checklist.md before Hub upload.")


if __name__ == "__main__":
    main()
