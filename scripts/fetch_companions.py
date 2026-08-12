"""Download public-domain companion texts from Project Gutenberg."""

from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "companion"

BOOKS = {
    "veblen_leisure_class.txt": "https://www.gutenberg.org/ebooks/833.txt.utf-8",
    "ruskin_unto_this_last.txt": "https://www.gutenberg.org/ebooks/36541.txt.utf-8",
    "carlyle_past_and_present.txt": "https://www.gutenberg.org/ebooks/26159.txt.utf-8",
    "george_progress_and_poverty.txt": "https://www.gutenberg.org/ebooks/55308.txt.utf-8",
    "london_people_of_the_abyss.txt": "https://www.gutenberg.org/ebooks/1688.txt.utf-8",
    "riis_how_the_other_half_lives.txt": "https://www.gutenberg.org/ebooks/45502.txt.utf-8",
}

UA = "Welles-research/0.1 (educational writing; n0social)"


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as response:
        dest.write_bytes(response.read())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, url in BOOKS.items():
        dest = OUT / name
        print(f"Fetching {name}...")
        try:
            download(url, dest)
            print(f"  {dest} ({dest.stat().st_size:,} bytes)")
        except Exception as exc:
            print(f"  FAILED {url}: {exc}")


if __name__ == "__main__":
    main()
