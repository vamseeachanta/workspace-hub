"""Tests for the name-agnostic redaction engine (scripts/legal/redact-client-pii.py).

These tests use SYNTHETIC names only — never real client identifiers — so the
test file itself carries no PII (the same constraint as the redactor script).
"""
import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_PATH = Path(__file__).resolve().parents[1] / "redact-client-pii.py"
_spec = importlib.util.spec_from_file_location("redact_client_pii", _MOD_PATH)
redact = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = redact  # let @dataclass resolve its module during exec
_spec.loader.exec_module(redact)


def _rules(yaml_text: str, tmp_path: Path):
    p = tmp_path / "map.yaml"
    p.write_text(yaml_text, encoding="utf-8")
    return redact.load_rules(p)


SYNTH_MAP = """
version: 1
rules:
  - {pattern: '/mnt/ace/alphacorp', replacement: '/mnt/ace/client-a', word_bound: false}
  - {pattern: 'alpha ?corp',        replacement: 'client-a', word_bound: false}
  - {pattern: 'beta',               replacement: 'client-b', word_bound: true}
"""


def test_basic_token_and_path(tmp_path):
    rules = _rules(SYNTH_MAP, tmp_path)
    text = "see /mnt/ace/alphacorp/docs and alphacorp and alpha corp"
    out, n = redact.redact_text(text, rules)
    assert "alphacorp" not in out.lower()
    assert "alpha corp" not in out.lower()
    assert "/mnt/ace/client-a/docs" in out
    assert n == 3


def test_case_insensitive(tmp_path):
    rules = _rules(SYNTH_MAP, tmp_path)
    out, n = redact.redact_text("AlphaCorp ALPHACORP", rules)
    assert "client-a client-a" == out
    assert n == 2


def test_word_bound_avoids_substring_collision(tmp_path):
    """'beta' is word-bound, so it must NOT match inside 'betatron' or 'alphabeta'."""
    rules = _rules(SYNTH_MAP, tmp_path)
    out, n = redact.redact_text("betatron alphabeta beta", rules)
    assert out == "betatron alphabeta client-b"
    assert n == 1


def test_word_bound_still_matches_across_underscore_digit_punct(tmp_path):
    """Alpha-boundary must still match a token abutting '_', digits, or punctuation
    (regression for the \\b-misses-on-underscore bug: 'beta_x', 'beta7', '_beta[')."""
    rules = _rules(SYNTH_MAP, tmp_path)
    out, n = redact.redact_text("beta_vessels.py beta7000 path/Beta[1].pdf", rules)
    assert "beta" not in out.lower()
    assert out == "client-b_vessels.py client-b7000 path/client-b[1].pdf"
    assert n == 3


def test_idempotent(tmp_path):
    rules = _rules(SYNTH_MAP, tmp_path)
    once, _ = redact.redact_text("alphacorp beta", rules)
    twice, n2 = redact.redact_text(once, rules)
    assert once == twice
    assert n2 == 0


def test_rule_order_more_specific_first(tmp_path):
    """Path rule (more specific) runs before the bare-token rule, so the path
    form is rewritten cleanly and the token rule doesn't double-touch it."""
    rules = _rules(SYNTH_MAP, tmp_path)
    out, _ = redact.redact_text("/mnt/ace/alphacorp/x", rules)
    assert out == "/mnt/ace/client-a/x"


def test_empty_rules_exits(tmp_path):
    p = tmp_path / "empty.yaml"
    p.write_text("version: 1\nrules: []\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        redact.load_rules(p)
