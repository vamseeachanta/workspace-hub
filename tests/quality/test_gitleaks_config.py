from __future__ import annotations

import tomllib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
FINGERPRINT_RE = re.compile(r"^[^:\n]+:[a-z0-9][a-z0-9-]*:\d+$")
ALLOWED_DIRECTORY_PATHS = {
    # Vendored static test assets; not authored repository code.
    r"^pylib/youtube_transcript_api/test/assets/",
}
WILDCARD_CHARS = {"[", "(", "|", "?"}


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


def _contains_unescaped_wildcard(pattern: str) -> bool:
    escaped = False
    for index, char in enumerate(pattern):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "." and index + 1 < len(pattern) and pattern[index + 1] in {"*", "+"}:
            return True
        if char in WILDCARD_CHARS:
            return True
    return False


def _assert_path_allowlist_is_narrow(paths: list[str]) -> None:
    for pattern in paths:
        if not pattern.startswith("^"):
            raise AssertionError(f"path allow-list entry is not anchored: {pattern}")
        if _contains_unescaped_wildcard(pattern):
            raise AssertionError(f"path allow-list entry contains wildcard syntax: {pattern}")
        if _path_is_directory_prefix(pattern):
            if pattern not in ALLOWED_DIRECTORY_PATHS:
                raise AssertionError(f"path allow-list directory is not approved: {pattern}")
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
        assert "not approved" in str(exc)
    else:
        raise AssertionError("bare top-level directory allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_extension_pattern() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^.*\.pem$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("extension path allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_wildcard_exact_file() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^.+$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("wildcard exact-file allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_wildcard_file_pattern() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^src/.*\.py$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("wildcard file allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unapproved_directory() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/plans/"])
    except AssertionError as exc:
        assert "not approved" in str(exc)
    else:
        raise AssertionError("unapproved directory allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unescaped_dot_star() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/.*$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("unescaped dot-star allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unescaped_dot_plus() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/.+$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("unescaped dot-plus allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unescaped_bracket() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/[abc]$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("unescaped bracket allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unescaped_parenthesis() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/(abc)$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("unescaped parenthesis allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unescaped_pipe() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/a|b$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("unescaped pipe allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_unescaped_question_mark() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/a?$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("unescaped question mark allow-list entry was accepted")


def test_gitleaks_path_allowlist_accepts_escaped_exact_file() -> None:
    _assert_path_allowlist_is_narrow([r"^docs/example\.md$"])


def test_gitleaks_path_allowlist_accepts_vendored_static_assets() -> None:
    _assert_path_allowlist_is_narrow([r"^pylib/youtube_transcript_api/test/assets/"])


def test_gitleaksignore_contains_only_fingerprints() -> None:
    ignore_path = ROOT / ".gitleaksignore"
    if not ignore_path.exists():
        # Older branches can omit the file; only validate it when present.
        return

    _assert_gitleaksignore_fingerprints(ignore_path.read_text(encoding="utf-8"))


def test_gitleaksignore_rejects_non_fingerprint_line() -> None:
    try:
        _assert_gitleaksignore_fingerprints("path:generic-api-key:12:extra")
    except AssertionError as exc:
        assert "fingerprints" in str(exc)
    else:
        raise AssertionError("non-fingerprint gitleaksignore line was accepted")
