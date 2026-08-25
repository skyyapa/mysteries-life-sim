from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def load_json(name: str) -> Any:
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_optional_json(name: str) -> Any | None:
    path = DATA_DIR / name
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
