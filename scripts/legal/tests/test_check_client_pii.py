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


# ── #3169: text mode (commit messages / PR metadata) ──────────────────────────
import os
import subprocess

_SCRIPT = _LEGAL / "check-client-pii.py"


def _write_map(tmp_path):
    p = tmp_path / "map.yaml"
    p.write_text(SYNTH_MAP, encoding="utf-8")
    return p


def _run_cli(args, stdin=None, env_extra=None):
    env = dict(os.environ)
    env.pop("LEGAL_PII_ALLOW", None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        input=stdin, capture_output=True, text=True, env=env,
    )
    return r.returncode, r.stdout, r.stderr


def test_scan_text_clean_returns_zero(tmp_path):
    rules = _rules(tmp_path)
    assert guard.scan_text("fix(loader): refactor parsing", rules, "commit abc123") == 0


def test_scan_text_detects_identifier(tmp_path):
    rules = _rules(tmp_path)
    assert guard.scan_text("rename alphacorp dir", rules, "commit abc123") == 1


def test_scan_text_withholds_value(tmp_path, capsys):
    """The matched token (and its codename) must never appear in output."""
    rules = _rules(tmp_path)
    rc = guard.scan_text("touch alphacorp config", rules, "commit deadbee")
    out = capsys.readouterr()
    blob = out.out + out.err
    assert rc == 1
    assert "alphacorp" not in blob
    assert "client-a" not in blob
    assert "commit deadbee" in blob  # source label IS shown


def test_message_file_dirty_blocks(tmp_path):
    m = _write_map(tmp_path)
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text("wip: move alphacorp things\n", encoding="utf-8")
    rc, _out, _err = _run_cli(["--message-file", str(msg), "--map", str(m), "--source", "commit X"])
    assert rc == 1


def test_message_file_clean_passes(tmp_path):
    m = _write_map(tmp_path)
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text("wip: tidy the loader\n", encoding="utf-8")
    rc, _out, _err = _run_cli(["--message-file", str(msg), "--map", str(m)])
    assert rc == 0


def test_stdin_dirty_blocks(tmp_path):
    m = _write_map(tmp_path)
    rc, _out, _err = _run_cli(["--stdin", "--map", str(m)], stdin="see alphacorp\n")
    assert rc == 1


def test_stdin_clean_passes(tmp_path):
    m = _write_map(tmp_path)
    rc, _out, _err = _run_cli(["--stdin", "--map", str(m)], stdin="nothing to see\n")
    assert rc == 0


def test_text_mode_degrade_open_no_map(tmp_path):
    missing = tmp_path / "nope.yaml"
    rc, _out, _err = _run_cli(["--stdin", "--map", str(missing)], stdin="alphacorp\n")
    assert rc == 0  # non-strict + missing map → degrade-open


def test_text_mode_strict_no_map(tmp_path):
    missing = tmp_path / "nope.yaml"
    rc, _out, _err = _run_cli(["--stdin", "--strict", "--map", str(missing)], stdin="alphacorp\n")
    assert rc == 2  # strict + missing map → exit 2


def test_commit_msg_hook_path(tmp_path):
    """Exercise exactly what the commit-msg hook runs: --message-file "$1"."""
    m = _write_map(tmp_path)
    dirty = tmp_path / "msg_dirty"
    dirty.write_text("squash: alphacorp cleanup\n", encoding="utf-8")
    clean = tmp_path / "msg_clean"
    clean.write_text("squash: cleanup\n", encoding="utf-8")
    rc_dirty, _o, _e = _run_cli(["--message-file", str(dirty), "--map", str(m)])
    rc_clean, _o, _e = _run_cli(["--message-file", str(clean), "--map", str(m)])
    assert rc_dirty == 1 and rc_clean == 0
