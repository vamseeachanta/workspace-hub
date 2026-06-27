"""TDD tests for #3255 — memory_freshness matrix verdict (epic #3248).

Targets build_equality_matrix.memory_freshness_verdict, which RECOMPUTES staleness at build time
(worst surface age + time since the audit) so a dead audit cron ages the cell — the same
dead-man's-switch as session_curation. Uses a fixed `now` for determinism.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "build-equality-matrix.py"

spec = importlib.util.spec_from_file_location("build_equality_matrix", MODULE_PATH)
assert spec is not None and spec.loader is not None
bem = importlib.util.module_from_spec(spec)
sys.modules["build_equality_matrix"] = bem
spec.loader.exec_module(bem)

NOW = datetime(2026, 6, 26, 12, 0, 0, tzinfo=timezone.utc)


def _rep(audited="2026-06-26T12:00:00+00:00", worst=0.0) -> dict:
    return {"dimensions": {"memory_freshness": {"audited_at": audited, "worst_age_hours": worst}}}


# ── recompute: current_age = worst_age + (now - audited) ──
def test_fresh_when_recent():
    assert bem.memory_freshness_verdict(_rep(worst=10.0), now=NOW) == "MEMORY-FRESH"


def test_fresh_at_threshold():
    assert bem.memory_freshness_verdict(_rep(worst=36.0), now=NOW) == "MEMORY-FRESH"


def test_stale_past_36h():
    assert bem.memory_freshness_verdict(_rep(worst=40.0), now=NOW) == "MEMORY-STALE"


def test_stale_at_72h():
    assert bem.memory_freshness_verdict(_rep(worst=72.0), now=NOW) == "MEMORY-STALE"


def test_expired_past_72h():
    assert bem.memory_freshness_verdict(_rep(worst=100.0), now=NOW) == "MEMORY-EXPIRED"


def test_dead_audit_ages_the_cell():
    # audit ran 50h ago (2026-06-24T10:00 → 2026-06-26T12:00) reporting worst=10h → current age
    # 60h → STALE (the dead-man's-switch: the frozen state file can't stay falsely green)
    assert bem.memory_freshness_verdict(
        _rep(audited="2026-06-24T10:00:00+00:00", worst=10.0), now=NOW) == "MEMORY-STALE"


# ── fail-closed ──
def test_missing_dimension():
    assert bem.memory_freshness_verdict({"dimensions": {}}, now=NOW) == "MISSING-EVIDENCE"


def test_non_dict():
    for bad in ("x", 1, None, ["a"]):
        assert bem.memory_freshness_verdict({"dimensions": {"memory_freshness": bad}}, now=NOW) == "MISSING-EVIDENCE"


def test_missing_or_garbled_fields():
    assert bem.memory_freshness_verdict({"dimensions": {"memory_freshness": {"worst_age_hours": 1.0}}}, now=NOW) == "MISSING-EVIDENCE"
    assert bem.memory_freshness_verdict({"dimensions": {"memory_freshness": {"audited_at": "2026-06-26T12:00:00+00:00"}}}, now=NOW) == "MISSING-EVIDENCE"
    assert bem.memory_freshness_verdict(_rep(audited="nope", worst=1.0), now=NOW) == "MISSING-EVIDENCE"
    assert bem.memory_freshness_verdict(_rep(worst=True), now=NOW) == "MISSING-EVIDENCE"  # bool not a number


def test_future_or_negative_failclosed():
    assert bem.memory_freshness_verdict(_rep(audited="2026-06-26T18:00:00+00:00", worst=1.0), now=NOW) == "MISSING-EVIDENCE"
    assert bem.memory_freshness_verdict(_rep(worst=-5.0), now=NOW) == "MISSING-EVIDENCE"


# ── wiring ──
def test_wiring():
    assert "memory_freshness" in bem.BASE_DISPLAY_DIMS
    assert "memory_freshness" in bem.DISPLAY_DIMS
    assert "MEMORY-FRESH" in bem.OK_VERDICTS
    groups = {g[0]: g for g in bem.GROUPS}
    assert groups["memory-freshness"][2] == ["memory_freshness"]
    sev = bem.ROLLUP_SEVERITY
    assert sev["MEMORY-EXPIRED"] > sev["MEMORY-STALE"] > sev["MEMORY-FRESH"] == 0
