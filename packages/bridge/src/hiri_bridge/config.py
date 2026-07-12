from __future__ import annotations

import os
from pathlib import Path


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    raw = os.getenv("HIRI_DATA_DIR", "data")
    path = Path(raw)
    if not path.is_absolute():
        path = package_root() / path
    path.mkdir(parents=True, exist_ok=True)
    return path


OUT_DIR = data_dir() / "out"
REGISTRY_PATH = data_dir() / "devices.json"
