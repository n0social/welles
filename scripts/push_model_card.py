"""Upload hub/README.md to n0social/welles (model card). Run on Colab or any machine with the token."""

from __future__ import annotations

from getpass import getpass
from pathlib import Path

from huggingface_hub import HfApi, login

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "hub" / "README.md"
REPO = "n0social/welles"


def main() -> None:
    if not CARD.exists():
        raise SystemExit(f"Missing {CARD}")
    login(token=getpass("Hugging Face write token (hidden): "))
    api = HfApi()
    api.upload_file(
        path_or_fileobj=str(CARD),
        path_in_repo="README.md",
        repo_id=REPO,
        repo_type="model",
        commit_message="docs: full Welles Architect model card",
    )
    print(f"Updated https://huggingface.co/{REPO}")


if __name__ == "__main__":
    main()
