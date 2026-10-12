from __future__ import annotations

import tomllib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
FINGERPRINT_RE = re.compile(r"^[^:\n]+:[a-z0-9][a-z0-9-]*:\d+$")


def _load_config(text: str) -> dict:
    config = tomllib.loads(text)
    extend = config.get("extend")
    if not isinstance(extend, dict) or extend.get("useDefault") is not True:
        raise AssertionError("gitleaks config must extend the default rules")
    return config


def _regexes_from_allowlist(allowlist: object) -> list[str]:
    if not isinstance(allowlist, dict):
        return []
    regexes = allowlist.get("regexes", [])
    if regexes is None:
        return []
    if not isinstance(regexes, list):
        raise AssertionError("allow-list regexes must be a list")
    return regexes


def _assert_no_allowlist_regexes(config: dict) -> None:
    regexes = list(_regexes_from_allowlist(config.get("allowlist")))

    for allowlist in config.get("allowlists", []):
        regexes.extend(_regexes_from_allowlist(allowlist))

    for rule in config.get("rules", []):
        regexes.extend(_regexes_from_allowlist(rule.get("allowlist")))
        for allowlist in rule.get("allowlists", []):
            regexes.extend(_regexes_from_allowlist(allowlist))

    if regexes:
        raise AssertionError("gitleaks config must not use allow-list regexes")


def _path_is_directory_prefix(pattern: str) -> bool:
    return pattern.endswith("/") and not pattern.endswith("$")


def _assert_path_allowlist_is_narrow(paths: list[str]) -> None:
    for pattern in paths:
        if not pattern.startswith("^"):
            raise AssertionError(f"path allow-list entry is not anchored: {pattern}")
        if pattern.startswith("^.*"):
            raise AssertionError(f"path allow-list entry is an extension pattern: {pattern}")
        if _path_is_directory_prefix(pattern):
            if pattern[1:].count("/") < 2:
                raise AssertionError(f"path allow-list entry is too broad: {pattern}")
        elif not pattern.endswith("$"):
            raise AssertionError(f"single-file path allow-list is not exact: {pattern}")


def _assert_gitleaksignore_fingerprints(text: str) -> None:
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if len(line) > 240 or not FINGERPRINT_RE.fullmatch(line):
            raise AssertionError("gitleaksignore must contain only fingerprints")


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


def test_gitleaks_config_does_not_use_allowlist_regexes() -> None:
    config_text = (ROOT / ".gitleaks.toml").read_text(encoding="utf-8")
    config = _load_config(config_text)

    _assert_no_allowlist_regexes(config)


def test_gitleaks_config_rejects_global_allowlist_regexes() -> None:
    config = {"allowlist": {"regexes": ["example"]}}

    try:
        _assert_no_allowlist_regexes(config)
    except AssertionError as exc:
        assert "allow-list regexes" in str(exc)
    else:
        raise AssertionError("global allow-list regex was accepted")


def test_gitleaks_config_rejects_rule_allowlist_regexes() -> None:
    config = {"rules": [{"allowlists": [{"regexes": ["example"]}]}]}

    try:
        _assert_no_allowlist_regexes(config)
    except AssertionError as exc:
        assert "allow-list regexes" in str(exc)
    else:
        raise AssertionError("rule allow-list regex was accepted")


def test_gitleaks_path_allowlist_entries_are_narrow() -> None:
    config_text = (ROOT / ".gitleaks.toml").read_text(encoding="utf-8")
    config = _load_config(config_text)

    _assert_path_allowlist_is_narrow(config["allowlist"]["paths"])


def test_gitleaks_path_allowlist_rejects_unanchored_entry() -> None:
    try:
        _assert_path_allowlist_is_narrow(["scripts/security/tests/"])
    except AssertionError as exc:
        assert "not anchored" in str(exc)
    else:
        raise AssertionError("unanchored path allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_non_exact_file() -> None:
    try:
        _assert_path_allowlist_is_narrow(["^scripts/example.py"])
    except AssertionError as exc:
        assert "not exact" in str(exc)
    else:
        raise AssertionError("non-exact file path allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_bare_top_level_directory() -> None:
    try:
        _assert_path_allowlist_is_narrow(["^docs/"])
    except AssertionError as exc:
        assert "too broad" in str(exc)
    else:
        raise AssertionError("bare top-level directory allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_extension_pattern() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^.*\.pem$"])
    except AssertionError as exc:
        assert "extension pattern" in str(exc)
    else:
        raise AssertionError("extension path allow-list entry was accepted")


def test_gitleaksignore_contains_only_fingerprints() -> None:
    ignore_path = ROOT / ".gitleaksignore"
    if not ignore_path.exists():
        return

    _assert_gitleaksignore_fingerprints(ignore_path.read_text(encoding="utf-8"))


def test_gitleaksignore_rejects_non_fingerprint_line() -> None:
    try:
        _assert_gitleaksignore_fingerprints("path:generic-api-key:12:extra")
    except AssertionError as exc:
        assert "fingerprints" in str(exc)
    else:
        raise AssertionError("non-fingerprint gitleaksignore line was accepted")
