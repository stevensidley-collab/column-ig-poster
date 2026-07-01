"""Append-only log of past posts (title, date, URL) kept in the repo for reference."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_PATH = REPO_ROOT / "posts_history.json"


def append_post(title: str, url: str, image_path: str, caption_path: str) -> None:
    entries = []
    if HISTORY_PATH.exists():
        entries = json.loads(HISTORY_PATH.read_text())

    entries.append(
        {
            "title": title,
            "url": url,
            "date": datetime.now(timezone.utc).isoformat(),
            "image_path": image_path,
            "caption_path": caption_path,
        }
    )
    HISTORY_PATH.write_text(json.dumps(entries, indent=2) + "\n")


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text())
