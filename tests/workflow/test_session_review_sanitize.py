"""Tests for the #3298 session-review sanitization gate.

Core scrub/verify functions are pure (take an explicit patterns list) — no
network, pytest-socket safe. Only load_deny_patterns touches yaml.
"""
import sys
from pathlib import Path

import pytest

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import session_review_sanitize as sani  # noqa: E402

PATTERNS = [("Synthco Field", False), ("Zephyr7", True)]


def test_sanitize_text_redacts_case_insensitive_pattern():
    out = sani.sanitize_text("Worked on synthco field risers", PATTERNS)
    assert "synthco field" not in out.lower()
    assert sani.REDACTION in out


def test_sanitize_text_respects_case_sensitive_pattern():
    # case_sensitive=True: exact case redacted, other case left alone
    assert sani.REDACTION in sani.sanitize_text("Zephyr7", PATTERNS)
    assert sani.sanitize_text("zephyr7", PATTERNS) == "zephyr7"


def test_sanitize_text_scrubs_abs_paths_ips_hosts():
    out = sani.sanitize_text(
        "ran on ace-linux-1 at /mnt/local-analysis/x via 192.168.1.5", PATTERNS)  # abs-path-allowed
    assert "/mnt/local-analysis" not in out  # abs-path-allowed
    assert "192.168.1.5" not in out
    assert "ace-linux-1" not in out
    assert "[path]" in out and "[ip]" in out and "[host]" in out


def test_find_violations_and_assert_clean():
    assert sani.find_violations("nothing sensitive here", PATTERNS) == []
    assert "Synthco Field" in sani.find_violations("Synthco Field deck", PATTERNS)
    with pytest.raises(sani.SanitizationError):
        sani.assert_clean("Synthco Field deck", PATTERNS)
    sani.assert_clean("clean text #123", PATTERNS)  # no raise


def test_sanitize_payload_deep():
    payload = {
        "title": "Zephyr7 work",
        "prs": [{"what": "fix for Synthco Field"}],
        "next_steps": ["email about Zephyr7"],
        "count": 5,
    }
    out = sani.sanitize_payload(payload, PATTERNS)
    assert "Zephyr7" not in out["title"]
    assert "Synthco Field" not in out["prs"][0]["what"]
    assert "Zephyr7" not in out["next_steps"][0]
    assert out["count"] == 5  # non-strings untouched


def test_load_deny_patterns_from_yaml(tmp_path):
    yaml_text = (
        'client_references:\n'
        '  - pattern: "Acme Field"\n'
        '    case_sensitive: false\n'
        'proprietary_tools: []\n'
        'client_infrastructure: []\n'
    )
    p = tmp_path / "deny.yaml"
    p.write_text(yaml_text)
    pats = sani.load_deny_patterns(p)
    assert ("Acme Field", False) in pats


def test_load_deny_patterns_tolerates_missing_sections(tmp_path):
    p = tmp_path / "deny.yaml"
    p.write_text('version: "2.0"\n')
    assert sani.load_deny_patterns(p) == []


def test_repo_deny_list_loads():
    repo_root = Path(__file__).resolve().parents[2]
    pats = sani.load_deny_patterns(repo_root / ".legal-deny-list.yaml")
    assert len(pats) > 0  # the real deny-list has client_references
