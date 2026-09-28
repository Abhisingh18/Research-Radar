"""Tracks which paper IDs have already been shown, so re-runs only surface new ones."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_STATE_FILE = Path.home() / ".research_radar" / "seen.json"


def load_seen(state_file: Path = DEFAULT_STATE_FILE) -> set[str]:
    if not state_file.exists():
        return set()
    try:
        return set(json.loads(state_file.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
        return set()


def save_seen(seen: set[str], state_file: Path = DEFAULT_STATE_FILE) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(sorted(seen)), encoding="utf-8")
