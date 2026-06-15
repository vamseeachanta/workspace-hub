"""Tests for the client-PII prevention guard (scripts/legal/check-client-pii.py).

Synthetic names only — the test file carries no real client identifiers.
"""
import importlib.util
import sys
from pathlib import Path

_LEGAL = Path(__file__).resolve().parents[1]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, _LEGAL / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


guard = _load("check_client_pii", "check-client-pii.py")
engine = _load("redact_client_pii", "redact-client-pii.py")

SYNTH_MAP = """
version: 1
rules:
  - {pattern: '/mnt/ace/alphacorp', replacement: '/mnt/ace/client-a', word_bound: false}
  - {pattern: 'alpha ?corp',        replacement: 'client-a', word_bound: false}
  - {pattern: 'beta',               replacement: 'client-b', word_bound: true}
"""


def _rules(tmp_path):
    p = tmp_path / "map.yaml"
    p.write_text(SYNTH_MAP, encoding="utf-8")
    return engine.load_rules(p)


def test_detects_violation_lines(tmp_path):
    rules = _rules(tmp_path)
    f = tmp_path / "doc.md"
    f.write_text("clean line\nthis mentions alphacorp here\nanother clean\nbeta too\n", encoding="utf-8")
    hits = guard.violations_in(f, rules)
    assert hits == [2, 4]


def test_clean_file_no_hits(tmp_path):
    rules = _rules(tmp_path)
    f = tmp_path / "ok.md"
    f.write_text("client-a and client-b are codenames, betatron is unrelated\n", encoding="utf-8")
    assert guard.violations_in(f, rules) == []


def test_word_bound_no_false_positive(tmp_path):
    """'beta' is word-bound → must not flag 'betatron'/'alphabeta'."""
    rules = _rules(tmp_path)
    f = tmp_path / "w.md"
    f.write_text("betatron alphabeta\n", encoding="utf-8")
    assert guard.violations_in(f, rules) == []


def test_binary_unreadable_skipped(tmp_path):
    rules = _rules(tmp_path)
    f = tmp_path / "b.bin"
    f.write_bytes(b"\xff\xfe alphacorp \x00")
    # non-utf8 → skipped, no crash
    assert guard.violations_in(f, rules) == []
