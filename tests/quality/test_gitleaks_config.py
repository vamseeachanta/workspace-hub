from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_config(text: str) -> dict:
    config = tomllib.loads(text)
    extend = config.get("extend")
    if not isinstance(extend, dict) or extend.get("useDefault") is not True:
        raise AssertionError("gitleaks config must extend the default rules")
    return config


def test_gitleaks_config_loads_default_rules() -> None:
    config_text = (ROOT / ".gitleaks.toml").read_text(encoding="utf-8")

    config = _load_config(config_text)

    assert config["extend"]["useDefault"] is True


def test_gitleaks_config_rejects_allowlist_without_rules() -> None:
    config_text = """
title = "example"

[allowlist]
paths = ['''^\\.gitleaks\\.toml$''']
"""

    try:
        _load_config(config_text)
    except AssertionError as exc:
        assert "default rules" in str(exc)
    else:
        raise AssertionError("config without default rules was accepted")


def test_gitleaks_self_path_allowlist_is_anchored() -> None:
    config_text = (ROOT / ".gitleaks.toml").read_text(encoding="utf-8")
    config = _load_config(config_text)

    paths = config["allowlist"]["paths"]
    assert r"^\.gitleaks\.toml$" in paths
