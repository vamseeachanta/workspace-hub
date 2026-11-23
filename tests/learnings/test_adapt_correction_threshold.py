"""TDD tests for #3256 (a) — adaptive correction-confidence threshold (epic #3248).

Targets scripts/learnings/adapt-correction-threshold.py: the PURE core
(``adapt_threshold`` / ``_is_human_terminal``) plus the thin CLI (``run_cli``). Pattern mirrors
tests/curation/test_detect_skill_drift.py (importlib spec load + a small fixture builder).

The loop is DORMANT BY DESIGN until a human-provenance ``reviewed_by`` marker exists on terminal
ledger entries (round-2 major #3). These tests assert the dormant hold on today's real ledger AND
the would-be adaptation behavior once such a marker lands.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "learnings" / "adapt-correction-threshold.py"

spec = importlib.util.spec_from_file_location("adapt_correction_threshold", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules["adapt_correction_threshold"] = mod
spec.loader.exec_module(mod)


# ── PURE CORE: adapt_threshold boundary / precedence / fail-safe matrix ────────
def test_hold_insufficient_sample():
    r = mod.adapt_threshold(current=80, accepted=4, rejected=1)  # terminal 5 < MIN_SAMPLE 8
    assert r["threshold"] == 80
    assert r["changed"] is False
    assert r["inputs"]["sample_sufficient"] is False


def test_lower_on_high_success():
    r = mod.adapt_threshold(current=90, accepted=10, rejected=1)  # rate ~0.91 >= 0.80
    assert r["threshold"] == 80
    assert r["changed"] is True
    assert "recall" in r["reason"]


def test_raise_on_low_success():
    r = mod.adapt_threshold(current=80, accepted=3, rejected=7)  # rate 0.30 <= 0.50
    assert r["threshold"] == 90
    assert r["changed"] is True
    assert "precision" in r["reason"]


def test_hold_in_dead_band():
    r = mod.adapt_threshold(current=80, accepted=6, rejected=4)  # rate 0.60 in dead-band
    assert r["threshold"] == 80
    assert r["changed"] is False


def test_floor_clamp():
    # already at FLOOR=80 with high success ⇒ cannot go below floor
    r = mod.adapt_threshold(current=80, accepted=10, rejected=0)
    assert r["threshold"] == 80
    assert r["changed"] is False


def test_ceiling_clamp():
    # already at CEIL=90 with low success ⇒ cannot exceed ceiling
    r = mod.adapt_threshold(current=90, accepted=0, rejected=10)
    assert r["threshold"] == 90
    assert r["changed"] is False


def test_step_lands_on_real_buckets():
    # the session_corrections lattice is exactly {80, 90}: never an off-lattice value
    lowered = mod.adapt_threshold(current=90, accepted=10, rejected=0)
    raised = mod.adapt_threshold(current=80, accepted=0, rejected=10)
    assert lowered["threshold"] in (80, 90)
    assert raised["threshold"] in (80, 90)


def test_min_sample_boundary_inclusive():
    # terminal == MIN_SAMPLE (8) exactly ⇒ adapts (not held)
    r = mod.adapt_threshold(current=90, accepted=8, rejected=0)
    assert r["inputs"]["sample_sufficient"] is True
    assert r["threshold"] == 80


def test_target_high_boundary_inclusive():
    # rate == 0.80 exactly ⇒ lowers
    r = mod.adapt_threshold(current=90, accepted=8, rejected=2)
    assert r["threshold"] == 80


def test_target_low_boundary_inclusive():
    # rate == 0.50 exactly ⇒ raises
    r = mod.adapt_threshold(current=80, accepted=5, rejected=5)
    assert r["threshold"] == 90


def test_current_none_uses_default():
    r = mod.adapt_threshold(current=None, accepted=1, rejected=1)  # insufficient ⇒ hold at default
    assert r["previous"] == 80
    assert r["threshold"] == 80


def test_current_garbled_uses_default():
    for bad in (True, "x", -5, 200, None, [1]):
        r = mod.adapt_threshold(current=bad, accepted=1, rejected=1)
        assert mod.FLOOR <= r["previous"] <= mod.CEIL          # always clamped into the band
    # explicitly non-numeric / bool / negative collapse to the default floor
    for bad in (True, "x", -5, None, [1]):
        assert mod.adapt_threshold(current=bad, accepted=1, rejected=1)["previous"] == 80


def test_pure_no_io(monkeypatch):
    # adapt_threshold must perform NO IO — monkeypatch open/subprocess to raise and still succeed
    import builtins
    import subprocess

    def _boom(*a, **k):
        raise AssertionError("adapt_threshold performed IO")

    monkeypatch.setattr(builtins, "open", _boom)
    monkeypatch.setattr(subprocess, "run", _boom)
    r = mod.adapt_threshold(current=80, accepted=6, rejected=4)
    assert r["threshold"] == 80


# ── human-provenance terminal gate (Rule 1) ───────────────────────────────────
def test_human_terminal_requires_reviewer():
    assert mod._is_human_terminal({"status": "accepted"}) is None  # no reviewed_by ⇒ not counted


def test_human_terminal_counts_with_reviewer():
    assert mod._is_human_terminal({"status": "accepted", "reviewed_by": "vamsee"}) == "survived"
    assert mod._is_human_terminal({"status": "rejected", "reviewed_by": "vamsee"}) == "rejected"


def test_blank_reviewer_not_human():
    assert mod._is_human_terminal({"status": "rejected", "reviewed_by": "  "}) is None
    assert mod._is_human_terminal({"status": "accepted", "reviewed_by": ""}) is None


def test_non_terminal_status_ignored_even_with_reviewer():
    # 'identified' is non-terminal: not counted even if a reviewer is present
    assert mod._is_human_terminal({"status": "identified", "reviewed_by": "vamsee"}) is None


# ── THIN CLI ───────────────────────────────────────────────────────────────────
def _write_ledger(tmp_path, entries) -> Path:
    import yaml
    p = tmp_path / "correction-promotions.yaml"
    p.write_text(yaml.safe_dump({"promotions": entries}))
    return p


def _run(tmp_path, ledger, *, state=None, stdout=False, notify_spy=None):
    state = state or (tmp_path / "correction-confidence-threshold.json")
    args = SimpleNamespace(ledger=str(ledger), state=str(state), stdout=stdout)
    rc = mod.run_cli(args)
    return rc, state


def test_cli_writes_json_and_exits_zero(tmp_path):
    entries = [{"status": "accepted", "reviewed_by": "vamsee"} for _ in range(8)]
    ledger = _write_ledger(tmp_path, entries)
    rc, state = _run(tmp_path, ledger)
    assert rc == 0
    doc = json.loads(state.read_text())
    assert doc["scope"] == "session_corrections"
    assert doc["schema_version"] == 1
    assert "threshold" in doc and "inputs" in doc


def test_cli_dormant_on_real_ledger(tmp_path):
    # today's real ledger: every entry status:identified, NO reviewed_by ⇒ 0 human-terminal
    real = REPO_ROOT / ".claude" / "state" / "candidates" / "correction-promotions.yaml"
    state = tmp_path / "state.json"
    args = SimpleNamespace(ledger=str(real), state=str(state), stdout=False)
    rc = mod.run_cli(args)
    assert rc == 0
    doc = json.loads(state.read_text())
    assert doc["threshold"] == 80
    assert doc["changed"] is False
    assert doc["dormant"] is True
    assert doc["inputs"]["terminal"] == 0


def test_cli_ignores_machine_written_status(tmp_path):
    # accepted/rejected present but NO reviewer (simulated sibling #3252 auto-write) ⇒ dormant
    entries = [{"status": "accepted"}, {"status": "rejected"}, {"status": "accepted"}]
    ledger = _write_ledger(tmp_path, entries)
    rc, state = _run(tmp_path, ledger)
    assert rc == 0
    doc = json.loads(state.read_text())
    assert doc["inputs"]["terminal"] == 0
    assert doc["dormant"] is True
    assert doc["threshold"] == 80


def test_cli_never_writes_status_label(tmp_path, monkeypatch):
    import subprocess

    def _no_subprocess(*a, **k):
        raise AssertionError("CLI shelled out (gh/git/status-label write)")

    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    entries = [{"status": "accepted", "reviewed_by": "v"} for _ in range(8)]
    ledger = _write_ledger(tmp_path, entries)
    rc, _ = _run(tmp_path, ledger)
    assert rc == 0


def test_cli_no_abs_paths_in_output(tmp_path):
    entries = [{"status": "accepted", "reviewed_by": "v"} for _ in range(8)]
    ledger = _write_ledger(tmp_path, entries)
    _, state = _run(tmp_path, ledger)
    raw = state.read_text()
    for needle in ("/home/", "/mnt/", "/Users/", "C:\\"):  # abs-path-allowed
        assert needle not in raw


def test_cli_always_exits_zero_on_garbled_ledger(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("{not: valid: yaml: [")
    state = tmp_path / "s.json"
    rc = mod.run_cli(SimpleNamespace(ledger=str(bad), state=str(state), stdout=False))
    assert rc == 0
    doc = json.loads(state.read_text())
    assert doc["threshold"] == 80  # fail-safe to default


def test_cli_stdout_does_not_write_state(tmp_path, capsys):
    entries = [{"status": "accepted", "reviewed_by": "v"} for _ in range(8)]
    ledger = _write_ledger(tmp_path, entries)
    state = tmp_path / "should-not-exist.json"
    rc = mod.run_cli(SimpleNamespace(ledger=str(ledger), state=str(state), stdout=True))
    assert rc == 0
    assert not state.exists()
    out = capsys.readouterr().out
    assert json.loads(out)["scope"] == "session_corrections"
