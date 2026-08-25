from __future__ import annotations

import json
from pathlib import Path

from .models import GameState


ROOT = Path(__file__).resolve().parents[2]
SAVE_DIR = ROOT / "saves"


def save_game(state: GameState, name: str = "autosave.json") -> Path:
    SAVE_DIR.mkdir(exist_ok=True)
    path = SAVE_DIR / name
    with path.open("w", encoding="utf-8") as file:
        json.dump(state.to_dict(), file, ensure_ascii=False, indent=2)
    return path
