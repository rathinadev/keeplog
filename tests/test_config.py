import tempfile
from pathlib import Path

import pytest

from keeplog import config


@pytest.fixture(autouse=True)
def _temp_config(monkeypatch):
    tmpdir = Path(tempfile.mkdtemp())
    cfg_path = tmpdir / "config.json"
    monkeypatch.setattr(config, "CONFIG_PATH", cfg_path)
    yield
    for f in tmpdir.iterdir():
        f.unlink()
    tmpdir.rmdir()


def test_defaults():
    cfg = config.load()
    assert cfg["mode"] == "full"
    assert cfg["retention_days"] == 30


def test_save_and_load():
    config.save({"mode": "light", "retention_days": 7})
    cfg = config.load()
    assert cfg["mode"] == "light"
    assert cfg["retention_days"] == 7


def test_get():
    assert config.get("mode") == "full"
    assert config.get("retention_days") == 30


def test_set_key():
    config.set_key("mode", "light")
    assert config.get("mode") == "light"


def test_unknown_key():
    assert config.get("nonexistent") is None
