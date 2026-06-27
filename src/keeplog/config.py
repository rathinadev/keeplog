import json
import os
import sys
from pathlib import Path
from typing import Any


def _config_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "keeplog"


CONFIG_PATH = _config_dir() / "config.json"

_DEFAULTS = {
    "mode": "full",
    "retention_days": 30,
}


def load() -> dict:
    if not CONFIG_PATH.exists():
        return dict(_DEFAULTS)
    try:
        with open(CONFIG_PATH) as f:
            return {**_DEFAULTS, **json.load(f)}
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save(cfg: dict):
    _config_dir().mkdir(parents=True, exist_ok=True)
    merged = {**_DEFAULTS, **cfg}
    with open(CONFIG_PATH, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")


def get(key: str) -> Any:
    return load().get(key, _DEFAULTS.get(key))


def set_key(key: str, value: Any):
    cfg = load()
    cfg[key] = value
    save(cfg)
