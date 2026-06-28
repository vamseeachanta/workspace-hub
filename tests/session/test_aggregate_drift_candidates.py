"""
ABOUTME: Unit tests for aggregate_drift_candidates.py — recurring-drift → parked skill-update candidates (#3254)
ABOUTME: Targets the pure recurrence core + merge logic with injected `now`/in-memory dicts, plus thin-CLI behavior
"""

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

# Import the underscore-named module via importlib (matches the sibling tests/session idiom).
_MODULE_PATH = (
    Path(__file__).parent.parent.parent
    / "scripts"
    / "session"
    / "aggregate_drift_candidates.py"
)
_spec = importlib.util.spec_from_file_location("aggregate_drift_candidates", _MODULE_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

evaluate_recurring = _mod.evaluate_recurring
merge_candidates = _mod.merge_candidates
parse_iso = _mod.parse_iso
iso_z = _mod.iso_z
main = _mod.main
DEFAULT_WINDOW_DAYS = _mod.DEFAULT_WINDOW_DAYS
DEFAULT_RECUR_DAYS = _mod.DEFAULT_RECUR_DAYS
LEAF_VIOLATION_CLASSES = _mod.LEAF_VIOLATION_CLASSES
CLASS_TARGETS = _mod.CLASS_TARGETS


# ─── Helpers ──────────────────────────────────────────────────────────────────

NOW = datetime(2026, 6, 27, 7, 0, 0)  # naive UTC, matches producer/CLI clock


def rec(scanned_at, *, log="L", provider="claude", **violations):
    """Build a drift-summary record. `scanned_at` may be a datetime or an ISO-Z string."""
    if isinstance(scanned_at, datetime):
        scanned_at = iso_z(scanned_at)
    full = {
        "python_runtime": 0,
        "file_placement": 0,
        "git_workflow": 0,
        "git_non_conventional": 0,
        "git_missing_wrk_ref": 0,
        "git_exempt_type": 0,
    }
    full.update(violations)
    return {"scanned_at": scanned_at, "log": log, "provider": provider, "violations": full}


def day(n, **kw):
    """A record stamped n days before NOW (distinct calendar dates for distinct n)."""
    return rec(NOW - timedelta(days=n), **kw)


def classes(out):
    return {c["drift_class"] for c in out}


def by_class(out):
    return {c["drift_class"]: c for c in out}


# ─── Pure-core: recurrence threshold ──────────────────────────────────────────

def test_recurring_at_day_threshold():
    # python_runtime>0 on exactly 3 distinct dates, recur_days=3 -> recurring
    entries = [
        day(0, log="a", python_runtime=5),
        day(1, log="b", python_runtime=3),
        day(2, log="c", python_runtime=4),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert classes(out) == {"python_runtime"}
    assert by_class(out)["python_runtime"]["distinct_days"] == 3


def test_below_day_threshold_not_recurring():
    # Only 2 distinct days < recur_days=3 -> nothing
    entries = [
        day(0, log="a", python_runtime=5),
        day(1, log="b", python_runtime=3),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert out == []


def test_single_noisy_night_many_sessions_not_recurring():
    # 50 distinct logs ALL sharing one scanned_at date = 1 distinct day < 3 -> not recurring (round-2 MAJOR)
    entries = [
        rec(NOW - timedelta(days=1), log=f"rollout-{i}", provider="codex", python_runtime=9)
        for i in range(50)
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert out == []


def test_window_excludes_old_records():
    # nonzero on 5 dates but 3 of them older than window -> only 2 in-window days < 3
    entries = [
        day(0, log="a", python_runtime=1),
        day(1, log="b", python_runtime=1),
        day(20, log="c", python_runtime=1),
        day(21, log="d", python_runtime=1),
        day(22, log="e", python_runtime=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert out == []


def test_future_scanned_at_skipped():
    # a record stamped in the future is ignored (clock-skew guard)
    entries = [
        day(0, log="a", python_runtime=1),
        day(1, log="b", python_runtime=1),
        rec(NOW + timedelta(days=2), log="future", python_runtime=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert out == []  # only 2 valid days


def test_distinct_session_dedup_max_count():
    # same log re-scanned counts once (max count) in EVIDENCE; days still distinct
    entries = [
        rec(NOW - timedelta(days=0), log="same", python_runtime=5),
        rec(NOW - timedelta(days=1), log="same", python_runtime=117),
        rec(NOW - timedelta(days=2), log="same", python_runtime=10),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    c = by_class(out)["python_runtime"]
    assert c["distinct_sessions"] == 1
    assert c["total_violations"] == 117  # max over the single deduped session
    assert c["distinct_days"] == 3


def test_rollup_git_workflow_excluded():
    # git_workflow (rollup) must never produce a candidate even if nonzero on many days
    entries = [day(n, log=f"l{n}", git_workflow=9) for n in range(9)]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert "git_workflow" not in classes(out)
    assert out == []


def test_exempt_type_excluded():
    entries = [day(n, log=f"l{n}", git_exempt_type=9) for n in range(9)]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert out == []


def test_leaf_git_classes_recur_independently():
    entries = [
        day(0, log="a", git_non_conventional=1, git_missing_wrk_ref=1),
        day(1, log="b", git_non_conventional=1, git_missing_wrk_ref=1),
        day(2, log="c", git_non_conventional=1, git_missing_wrk_ref=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert classes(out) == {"git_non_conventional", "git_missing_wrk_ref"}


def test_cross_provider_days_combine():
    # provider volume must not swamp; days combine across providers
    entries = [
        rec(NOW - timedelta(days=0), log="x", provider="codex", python_runtime=1),
        rec(NOW - timedelta(days=1), log="y", provider="claude", python_runtime=1),
        rec(NOW - timedelta(days=2), log="z", provider="hermes", python_runtime=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert by_class(out)["python_runtime"]["distinct_days"] == 3


def test_zero_and_nonint_counts_treated_as_zero():
    entries = [
        rec(NOW - timedelta(days=0), log="a", python_runtime="x"),
        rec(NOW - timedelta(days=1), log="b", python_runtime=None),
        rec(NOW - timedelta(days=2), log="c", python_runtime=-1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert out == []


def test_malformed_scanned_at_skipped():
    entries = [
        {"scanned_at": "yesterday", "log": "a", "provider": "claude",
         "violations": {"python_runtime": 9}},
        {"scanned_at": "", "log": "b", "provider": "claude",
         "violations": {"python_runtime": 9}},
        day(0, log="c", python_runtime=1),
        day(1, log="d", python_runtime=1),
        day(2, log="e", python_runtime=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    # the 3 valid days still produce a candidate; malformed records ignored, no raise
    assert by_class(out)["python_runtime"]["distinct_days"] == 3


def test_emitted_timestamps_roundtrip():
    entries = [
        day(0, log="a", python_runtime=1),
        day(1, log="b", python_runtime=1),
        day(2, log="c", python_runtime=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    c = by_class(out)["python_runtime"]
    for key in ("first_seen", "last_seen"):
        assert c[key].endswith("Z")
        assert "+00:00" not in c[key]
        assert parse_iso(c[key]) is not None


def test_empty_summary_no_candidates():
    assert evaluate_recurring([], now=NOW, window_days=14, recur_days=3) == []


def test_provider_breakdown_recorded():
    entries = [
        rec(NOW - timedelta(days=0), log="a", provider="claude", python_runtime=1),
        rec(NOW - timedelta(days=1), log="b", provider="claude", python_runtime=1),
        rec(NOW - timedelta(days=2), log="c", provider="codex", python_runtime=1),
    ]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    assert by_class(out)["python_runtime"]["providers"] == {"claude": 2, "codex": 1}


def test_class_target_mapping():
    entries = [day(n, log=f"l{n}", python_runtime=1) for n in range(3)]
    out = evaluate_recurring(entries, now=NOW, window_days=14, recur_days=3)
    c = by_class(out)["python_runtime"]
    assert c["target"] == CLASS_TARGETS["python_runtime"][0]
    assert c["kind"] == "skill-guide"


# ─── Merge: human-status preservation + aging ─────────────────────────────────

def _fresh(cls="python_runtime", days=3):
    return [{
        "drift_class": cls, "kind": "skill-guide",
        "target": CLASS_TARGETS[cls][0], "action": "act",
        "distinct_days": days, "distinct_sessions": days,
        "total_violations": 10, "providers": {"claude": days},
        "first_seen": "2026-06-20T07:00:00Z", "last_seen": "2026-06-27T07:00:00Z",
        "window_days": 14, "rationale": "r",
    }]


def test_merge_inserts_new_class():
    doc = merge_candidates(None, _fresh(), now_iso="2026-06-27T07:00:00Z",
                           machine="m", window_days=14, recur_days=3)
    rows = by_class(doc["candidates"])
    assert rows["python_runtime"]["status"] == "candidate"
    assert rows["python_runtime"]["active"] is True


def test_merge_preserves_human_status():
    existing = {"candidates": [{"drift_class": "python_runtime", "status": "dismissed",
                                "active": True, "distinct_days": 1, "first_seen": "2026-06-01T07:00:00Z"}]}
    doc = merge_candidates(existing, _fresh(days=5), now_iso="2026-06-27T07:00:00Z",
                           machine="m", window_days=14, recur_days=3)
    row = by_class(doc["candidates"])["python_runtime"]
    assert row["status"] == "dismissed"            # never clobbered
    assert row["distinct_days"] == 5                # evidence refreshed
    assert row["active"] is True


def test_merge_refreshes_candidate_evidence():
    existing = {"candidates": [{"drift_class": "python_runtime", "status": "candidate",
                                "active": False, "distinct_days": 3, "last_seen": "2026-06-10T07:00:00Z",
                                "first_seen": "2026-06-01T07:00:00Z"}]}
    doc = merge_candidates(existing, _fresh(days=7), now_iso="2026-06-27T07:00:00Z",
                           machine="m", window_days=14, recur_days=3)
    row = by_class(doc["candidates"])["python_runtime"]
    assert row["status"] == "candidate"
    assert row["distinct_days"] == 7
    assert row["last_seen"] == "2026-06-27T07:00:00Z"
    assert row["active"] is True


def test_merge_candidate_falls_below_threshold_marked_stale():
    existing = {"candidates": [{"drift_class": "python_runtime", "status": "candidate",
                                "active": True, "distinct_days": 4, "last_seen": "2026-06-15T07:00:00Z",
                                "first_seen": "2026-06-01T07:00:00Z"}]}
    doc = merge_candidates(existing, [], now_iso="2026-06-27T07:00:00Z",
                           machine="m", window_days=14, recur_days=3)
    row = by_class(doc["candidates"])["python_runtime"]
    assert row["status"] == "candidate"            # not deleted
    assert row["active"] is False                  # aged out
    assert row["last_seen"] == "2026-06-15T07:00:00Z"  # left as-is (now out of window)


def test_merge_keeps_human_status_below_threshold_intact():
    existing = {"candidates": [{"drift_class": "python_runtime", "status": "promoted",
                                "active": True, "distinct_days": 9, "first_seen": "2026-06-01T07:00:00Z"}]}
    doc = merge_candidates(existing, [], now_iso="2026-06-27T07:00:00Z",
                           machine="m", window_days=14, recur_days=3)
    row = by_class(doc["candidates"])["python_runtime"]
    assert row["status"] == "promoted"             # untouched
    assert row["active"] is True                   # untouched (already triaged)


def test_first_seen_preserved_on_refresh():
    existing = {"candidates": [{"drift_class": "python_runtime", "status": "candidate",
                                "active": True, "first_seen": "2026-05-01T07:00:00Z"}]}
    doc = merge_candidates(existing, _fresh(), now_iso="2026-06-27T07:00:00Z",
                           machine="m", window_days=14, recur_days=3)
    row = by_class(doc["candidates"])["python_runtime"]
    assert row["first_seen"] == "2026-05-01T07:00:00Z"  # sticky older value


# ─── Thin CLI ─────────────────────────────────────────────────────────────────

@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    summary = tmp_path / "drift-summary.yaml"
    candidates = tmp_path / "drift-skill-candidates.yaml"
    monkeypatch.setenv("DRIFT_SUMMARY_FILE", str(summary))
    monkeypatch.setenv("DRIFT_CANDIDATES_FILE", str(candidates))
    monkeypatch.delenv("DRIFT_WINDOW_DAYS", raising=False)
    monkeypatch.delenv("DRIFT_RECUR_DAYS", raising=False)
    return summary, candidates


def _write_recurring_corpus(path, *, cls="python_runtime", days=4):
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    entries = [rec(now - timedelta(days=n), log=f"l{n}", **{cls: 9}) for n in range(days)]
    path.write_text(yaml.safe_dump(entries))


def test_cli_missing_summary_file_noop(cli_env):
    summary, candidates = cli_env
    rc = main([])
    assert rc == 0
    assert not candidates.exists() or yaml.safe_load(candidates.read_text())["candidates"] == []


def test_cli_garbled_summary_failcloses(cli_env):
    summary, candidates = cli_env
    summary.write_text("][")
    rc = main([])
    assert rc == 0
    if candidates.exists():
        assert yaml.safe_load(candidates.read_text())["candidates"] == []


def test_cli_always_exit_zero_on_candidates(cli_env):
    summary, candidates = cli_env
    _write_recurring_corpus(summary)
    rc = main([])
    assert rc == 0
    doc = yaml.safe_load(candidates.read_text())
    assert any(c["drift_class"] == "python_runtime" for c in doc["candidates"])


def test_cli_env_threshold_override(cli_env, monkeypatch):
    summary, candidates = cli_env
    _write_recurring_corpus(summary, days=4)  # 4 distinct days
    monkeypatch.setenv("DRIFT_RECUR_DAYS", "5")
    rc = main([])
    assert rc == 0
    doc = yaml.safe_load(candidates.read_text()) if candidates.exists() else {"candidates": []}
    assert doc["candidates"] == []  # 4 days < override 5


def test_cli_stdout_dry_run_no_write(cli_env, capsys):
    summary, candidates = cli_env
    _write_recurring_corpus(summary)
    rc = main(["--stdout"])
    assert rc == 0
    assert not candidates.exists()  # nothing written
    doc = yaml.safe_load(capsys.readouterr().out)
    assert doc["schema_version"] == 1


def test_cli_atomic_write(cli_env):
    summary, candidates = cli_env
    _write_recurring_corpus(summary)
    main([])
    doc = yaml.safe_load(candidates.read_text())
    assert "generated_at" in doc
    assert doc["recur_days"] == DEFAULT_RECUR_DAYS
    assert doc["schema_version"] == 1


def test_cli_uses_machine_label(cli_env, monkeypatch):
    summary, candidates = cli_env
    _write_recurring_corpus(summary)
    monkeypatch.setattr(_mod, "machine_label", lambda: "BOXLBL")
    main([])
    doc = yaml.safe_load(candidates.read_text())
    assert doc["machine"] == "BOXLBL"


def test_cli_production_import_resolves_machine_label(tmp_path):
    """Run the module as the nightly does (bare subprocess) — real sys.path.insert + import."""
    summary = tmp_path / "drift-summary.yaml"
    _write_recurring_corpus(summary)
    env = dict(os.environ, DRIFT_SUMMARY_FILE=str(summary))
    env.pop("DRIFT_RECUR_DAYS", None)
    env.pop("DRIFT_WINDOW_DAYS", None)
    proc = subprocess.run(
        [sys.executable, str(_MODULE_PATH), "--stdout"],
        capture_output=True, text=True, env=env, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "ModuleNotFoundError" not in proc.stderr
    doc = yaml.safe_load(proc.stdout)
    assert doc["machine"] == _mod.machine_label()
