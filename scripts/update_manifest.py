#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
MANIFEST_FILE = POSTS_DIR / "manifest.json"


def main() -> None:
    files = sorted(
        path.name
        for path in POSTS_DIR.glob("*.md")
        if path.is_file()
    )
    MANIFEST_FILE.write_text(
        json.dumps(files, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated {MANIFEST_FILE} with {len(files)} posts")


if __name__ == "__main__":
    main()
