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
        if re.fullmatch(r"\^[^/]+/\$?", pattern):
            raise AssertionError("path allow-list directory is not approved")
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


def _assert_reason_groups(text: str) -> None:
    reason = False
    entries = False
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            reason = entries = False
        elif line.startswith("#"):
            if entries:
                reason = entries = False
            if line.startswith("# Reason:") and line.removeprefix("# Reason:").strip():
                reason = True
        else:
            if not reason:
                raise AssertionError(f"fingerprint group needs a reason at line {number}")
            entries = True


def _assert_scan_provenance(text: str) -> None:
    plain = " ".join(re.sub(r"<[^>]+>", " ", text).split())
    if ("gitleaks dir . --config .gitleaks.toml" not in plain
            or not re.search(r"Configuration revision:\s+[0-9a-f]+\b", plain)):
        raise AssertionError("scan provenance needs a command and configuration revision")


def _assert_path_reasons(text: str) -> None:
    in_allowlist = in_paths = False
    previous = ""
    checked: list[str] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line.startswith("[") and not in_paths:
            in_allowlist = line == "[allowlist]"
        elif in_allowlist and re.fullmatch(r"paths\s*=\s*\[", line):
            in_paths = True
        elif in_paths and line == "]":
            in_paths = False
        elif in_paths and line and not line.startswith("#"):
            if not previous.startswith("#") or not previous[1:].strip():
                raise AssertionError(f"allow-list path needs a reason at line {number}")
            # One entry per line makes the comment-to-path association unambiguous.
            values = tomllib.loads("values = [" + line + "]")["values"]
            if len(values) != 1:
                raise AssertionError("each allow-list path needs its own reason")
            checked.extend(values)
        previous = line
    expected = tomllib.loads(text).get("allowlist", {}).get("paths", [])
    if checked != expected:
        raise AssertionError("allow-list paths need individual lines and reason comments")


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


@pytest.mark.parametrize("text", [
    '[extend]\nuseDefault = true\ndisabledRules = ["generic-api-key"]\n',
    '[extend]\nuseDefault = true\npath = "replacement.toml"\n',
    '[extend]\nuseDefault = true\nunknown = true\n',
    '[extend]\n',
    '[extend]\nuseDefault = false\n',
    '[extend]\nuseDefault = true\n[[rules]]\nid = "generic-api-key"\n',
    '[extend]\nuseDefault = true\n[[rules]]\nid = "new-example"\n',
])
def test_temporary_config_rejects_rule_replacement(tmp_path: Path, text: str) -> None:
    """Expected rejection: issue 4069 item 1, exact extension and no rule tables.

    The colliding identifier is from config/gitleaks.toml, generic-api-key,
    at https://github.com/gitleaks/gitleaks/tree/v8.21.2. Rejecting every
    custom table also protects defaults added by future scanner releases.
    TOML tables and booleans follow https://toml.io/en/v1.0.0.
    """
    config = tmp_path / "config.toml"
    config.write_text(text, encoding="utf-8")
    with pytest.raises(AssertionError):
        _load_config(config.read_text(encoding="utf-8"))


def test_ignore_groups_have_adjacent_reasons() -> None:
    """Issue 4069 item 2: each fingerprint group needs an explicit reason."""
    _assert_reason_groups((ROOT / ".gitleaksignore").read_text(encoding="utf-8"))


@pytest.mark.parametrize("text", [
    "file:generic-api-key:1\n",
    "# Group title only\nfile:generic-api-key:1\n",
    "# Reason: documentation example\na:generic-api-key:1\n\nb:generic-api-key:2\n",
    "# Reason: fixture\na:generic-api-key:1\n# Another group\nb:generic-api-key:2\n",
    "# Reason: \nfile:generic-api-key:1\n",
])
def test_ignore_groups_reject_missing_reasons(text: str) -> None:
    with pytest.raises(AssertionError, match="reason"):
        _assert_reason_groups(text)


def test_ignore_group_reason_covers_multiple_entries() -> None:
    _assert_reason_groups("# Reason: documentation example\n"
                          "a:generic-api-key:1\nb:generic-api-key:2\n")


def test_scan_note_records_command_configuration_revision_and_status() -> None:
    """Provenance comes from pull request 4051 and issue 4069 item 3."""
    _assert_scan_provenance((ROOT / "docs/security/secret-scanning-notes.html")
                            .read_text(encoding="utf-8"))


@pytest.mark.parametrize("missing", ["command", "revision"])
def test_scan_provenance_rejects_missing_basis(missing: str) -> None:
    command = "" if missing == "command" else "gitleaks dir . --config .gitleaks.toml"
    revision = "" if missing == "revision" else "Configuration revision: 9b745efc"
    with pytest.raises(AssertionError, match="provenance"):
        _assert_scan_provenance(f"{command} {revision} NOT_EVALUATED")


def test_allowlist_paths_have_individual_reasons() -> None:
    """Each path needs an adjacent reason under the requested hygiene contract."""
    _assert_path_reasons((ROOT / ".gitleaks.toml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("reason", ["", "#\n", "# Reason elsewhere\n\n"])
def test_allowlist_paths_reject_missing_adjacent_reason(reason: str) -> None:
    with pytest.raises(AssertionError, match="reason"):
        _assert_path_reasons("[allowlist]\npaths = [\n" + reason
                             + "'''^docs/example\\.md$''',\n]\n")


def test_allowlist_reason_does_not_cover_next_path() -> None:
    with pytest.raises(AssertionError, match="reason"):
        _assert_path_reasons("[allowlist]\npaths = [\n# Example documentation\n"
                             "'''^docs/first$''',\n'''^docs/second$''',\n]\n")


def test_allowlist_accepts_individual_reason() -> None:
    _assert_path_reasons("[allowlist]\npaths = [\n# Reviewed example documentation\n"
                         "'''^docs/example\\.md$''',\n]\n")


def test_allowlist_rejects_exact_top_level_directory() -> None:
    with pytest.raises(AssertionError, match="not approved"):
        _assert_path_allowlist_is_narrow(["^docs/$"])


def test_scanner_regressions_are_collected_by_ci() -> None:
    workflow = (ROOT / ".github/workflows/baseline-check.yml").read_text(encoding="utf-8")
    for test_file in ["test_gitleaks_config.py", "test_gitleaks_wrapper.py",
                      "test_gitleaks_runtime.py"]:
        assert "tests/quality/" + test_file in workflow
