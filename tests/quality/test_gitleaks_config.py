from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TREE_FINGERPRINT_RE = re.compile(r"^[^:\n]+:[a-z0-9][a-z0-9-]*:\d+$")
HISTORY_FINGERPRINT_RE = re.compile(r"^[0-9a-f]+:[^:\n]+:[a-z0-9][a-z0-9-]*:\d+$")
EXACT_PATH_RE = re.compile(r"^\^[A-Za-z0-9_/\-]*(?:\\[.-][A-Za-z0-9_/\-]*)*\$?$")
ALLOWED_DIRECTORY_PATHS = {
    # Vendored static test assets; not authored repository code.
    r"^pylib/youtube_transcript_api/test/assets/",
}
ALLOWED_ALLOWLIST_KEYS = {"description", "paths"}


def _load_config(text: str) -> dict:
    config = tomllib.loads(text)
    extend = config.get("extend")
    if not isinstance(extend, dict) or extend.get("useDefault") is not True:
        raise AssertionError("gitleaks config must extend the default rules")
    # Issue 4069: preserve every default rule; no alternate rule sources.
    if set(extend) != {"useDefault"}:
        raise AssertionError("gitleaks extend must contain only useDefault")
    if "rules" in config:
        raise AssertionError("gitleaks config must not declare custom rules")
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


def _allowlists_from_config(config: dict) -> list[dict]:
    allowlists: list[dict] = []
    allowlist = config.get("allowlist")
    if isinstance(allowlist, dict):
        allowlists.append(allowlist)

    for allowlist in config.get("allowlists", []):
        if isinstance(allowlist, dict):
            allowlists.append(allowlist)

    for rule in config.get("rules", []):
        if not isinstance(rule, dict):
            continue
        allowlist = rule.get("allowlist")
        if isinstance(allowlist, dict):
            allowlists.append(allowlist)
        for allowlist in rule.get("allowlists", []):
            if isinstance(allowlist, dict):
                allowlists.append(allowlist)

    return allowlists


def _assert_no_allowlist_regexes(config: dict) -> None:
    regexes: list[str] = []
    for allowlist in _allowlists_from_config(config):
        regexes.extend(_regexes_from_allowlist(allowlist))

    if regexes:
        raise AssertionError("gitleaks config must not use allow-list regexes")


def _assert_allowlist_tables_only_use_path_keys(config: dict) -> None:
    for allowlist in _allowlists_from_config(config):
        extra_keys = set(allowlist) - ALLOWED_ALLOWLIST_KEYS
        if extra_keys:
            raise AssertionError("gitleaks allow-list tables may only use paths")


def _path_allowlists_from_config(config: dict) -> list[str]:
    paths: list[str] = []
    for allowlist in _allowlists_from_config(config):
        table_paths = allowlist.get("paths", [])
        if table_paths is None:
            continue
        if not isinstance(table_paths, list):
            raise AssertionError("allow-list paths must be a list")
        paths.extend(table_paths)
    return paths


def _path_is_directory_prefix(pattern: str) -> bool:
    return pattern.endswith("/") and not pattern.endswith("$")


def _assert_path_allowlist_is_narrow(paths: list[str]) -> None:
    for pattern in paths:
        if not pattern.startswith("^"):
            raise AssertionError(f"path allow-list entry is not anchored: {pattern}")
        if not EXACT_PATH_RE.fullmatch(pattern):
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
        if len(line) > 240 or not (
            TREE_FINGERPRINT_RE.fullmatch(line) or HISTORY_FINGERPRINT_RE.fullmatch(line)
        ):
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


def test_gitleaks_config_allowlist_tables_only_use_paths() -> None:
    config_text = (ROOT / ".gitleaks.toml").read_text(encoding="utf-8")
    config = _load_config(config_text)

    _assert_allowlist_tables_only_use_path_keys(config)


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


def test_gitleaks_config_rejects_allowlist_commits_key() -> None:
    config = {"allowlist": {"paths": [r"^docs/example\.md$"], "commits": ["abc123"]}}

    try:
        _assert_allowlist_tables_only_use_path_keys(config)
    except AssertionError as exc:
        assert "only use paths" in str(exc)
    else:
        raise AssertionError("allow-list commits key was accepted")


def test_gitleaks_config_rejects_allowlist_stopwords_key() -> None:
    config = {"allowlists": [{"paths": [r"^docs/example\.md$"], "stopwords": ["example"]}]}

    try:
        _assert_allowlist_tables_only_use_path_keys(config)
    except AssertionError as exc:
        assert "only use paths" in str(exc)
    else:
        raise AssertionError("allow-list stopwords key was accepted")


def test_gitleaks_path_allowlist_entries_are_narrow() -> None:
    config_text = (ROOT / ".gitleaks.toml").read_text(encoding="utf-8")
    config = _load_config(config_text)

    _assert_path_allowlist_is_narrow(_path_allowlists_from_config(config))


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
        assert "not exact" in str(exc) or "wildcard" in str(exc)
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


def test_gitleaks_path_allowlist_rejects_escaped_non_space_wildcard() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^\S+$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("non-space wildcard allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_escaped_word_wildcard() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^\w+$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("word wildcard allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_brace_any_quantifier() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^.{1,}$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("brace wildcard allow-list entry was accepted")


def test_gitleaks_path_allowlist_rejects_brace_literal_quantifier() -> None:
    try:
        _assert_path_allowlist_is_narrow([r"^docs/a{1,2}$"])
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("brace quantifier allow-list entry was accepted")


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


def test_gitleaks_path_allowlist_rejects_rule_level_broad_path() -> None:
    config_text = """
title = "example"

[extend]
useDefault = true

[[rules]]
id = "example"
description = "example"
regex = '''example'''
  [rules.allowlist]
  paths = ['''^\\S+$''']
"""
    config = tomllib.loads(config_text)

    try:
        _assert_path_allowlist_is_narrow(_path_allowlists_from_config(config))
    except AssertionError as exc:
        assert "wildcard" in str(exc)
    else:
        raise AssertionError("rule-level broad path allow-list entry was accepted")


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


@pytest.mark.parametrize("extension", [
    'disabledRules = ["generic-api-key"]',
    'disabledRules = []',
    'path = "replacement.toml"',
])
def test_gitleaks_config_rejects_extra_extend_keys(extension: str) -> None:
    """Issue 4069: only useDefault is allowed, regardless of extra-key value."""
    with pytest.raises(AssertionError, match="only useDefault"):
        _load_config("[extend]\nuseDefault = true\n" + extension)


@pytest.mark.parametrize("rule_id", ["generic-api-key", "custom-example"])
def test_gitleaks_config_rejects_rule_tables(rule_id: str) -> None:
    """Issue 4069 permits rejecting all custom rules: both inputs must fail."""
    text = ('[extend]\nuseDefault = true\n\n[[rules]]\n'
            f'id = "{rule_id}"\nregex = "example"\n')
    with pytest.raises(AssertionError, match="custom rules"):
        _load_config(text)
