"""Tests for the session-curation freshness dimension on build-equality-matrix.py.

Covers freshness_verdict(report, now=<fixed datetime>) — the daily-freshness grading
family for the 'session_curation' dimension (CURATED-FRESH ≤12h · CURATED-STALE ≤24h ·
CURATED-EXPIRED >24h · MISSING-EVIDENCE on no/garbled/future stamp) — plus the
structural wiring (display dims, OK set, group, rollup severity ordering).

Module-loading idiom mirrors test_build_equality_matrix.py: the target is a kebab-case
file ('build-equality-matrix.py'), so it's loaded via importlib.util.spec_from_file_location
and registered in sys.modules BEFORE exec (kebab-case import safety).
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta

import pytest

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "build-equality-matrix.py"

spec = importlib.util.spec_from_file_location("build_equality_matrix", MODULE_PATH)
assert spec is not None and spec.loader is not None
bem = importlib.util.module_from_spec(spec)
sys.modules["build_equality_matrix"] = bem  # register BEFORE exec (kebab-case import safety)
spec.loader.exec_module(bem)


# ── fixtures ────────────────────────────────────────────────────────────────
# A fixed, deterministic "now" so age-of-stamp grading never depends on wall clock.
NOW = datetime(2026, 6, 26, 12, 0, 0)


def _report(stamp) -> dict:
    """A report whose session_curation cell carries `stamp` as last_curated_at."""
    return {"dimensions": {"session_curation": {
        "last_curated_at": stamp,
        "sessions_24h": 133,
        "providers_active": "claude,codex,gemini,hermes",
        "memory_files_changed": 200,
    }}}


def _report_aged(hours: float) -> dict:
    """A report whose last_curated_at is exactly `hours` before the fixed NOW."""
    return _report((NOW - timedelta(hours=hours)).isoformat())


# ── CURATED-FRESH (≤12h) ────────────────────────────────────────────────────
def test_fresh_at_1h():
    assert bem.freshness_verdict(_report_aged(1), now=NOW) == "CURATED-FRESH"


def test_fresh_at_exactly_12h_boundary_inclusive():
    # boundary is inclusive: exactly the stale threshold still grades FRESH
    assert bem.freshness_verdict(_report_aged(12), now=NOW) == "CURATED-FRESH"


# ── CURATED-STALE (>12h, ≤24h) ──────────────────────────────────────────────
def test_stale_at_12_5h():
    assert bem.freshness_verdict(_report_aged(12.5), now=NOW) == "CURATED-STALE"


def test_stale_at_exactly_24h_boundary_inclusive():
    assert bem.freshness_verdict(_report_aged(24), now=NOW) == "CURATED-STALE"


# ── CURATED-EXPIRED (>24h) ──────────────────────────────────────────────────
def test_expired_at_25h():
    assert bem.freshness_verdict(_report_aged(25), now=NOW) == "CURATED-EXPIRED"


def test_expired_at_100h():
    assert bem.freshness_verdict(_report_aged(100), now=NOW) == "CURATED-EXPIRED"


# ── MISSING-EVIDENCE (fail-closed) ──────────────────────────────────────────
def test_missing_evidence_no_session_curation_dim():
    assert bem.freshness_verdict({"dimensions": {}}, now=NOW) == "MISSING-EVIDENCE"


def test_missing_evidence_no_dimensions_key():
    assert bem.freshness_verdict({}, now=NOW) == "MISSING-EVIDENCE"


def test_missing_evidence_non_dict_dim():
    # a scalar / list where a dict block is expected must not flow into grading
    for bad in ("not-a-dict", ["list"], 42, None):
        assert bem.freshness_verdict(
            {"dimensions": {"session_curation": bad}}, now=NOW) == "MISSING-EVIDENCE", bad


def test_missing_evidence_missing_last_curated_at():
    rep = _report("placeholder")
    del rep["dimensions"]["session_curation"]["last_curated_at"]
    assert bem.freshness_verdict(rep, now=NOW) == "MISSING-EVIDENCE"


def test_missing_evidence_non_string_last_curated_at():
    for bad in (None, 1234567890, 12.5, ["2026-06-26T06:21:21"]):
        assert bem.freshness_verdict(_report(bad), now=NOW) == "MISSING-EVIDENCE", bad


def test_missing_evidence_garbled_last_curated_at():
    for garbled in ("not-a-timestamp", "2026-13-99T99:99:99", "yesterday", ""):
        assert bem.freshness_verdict(_report(garbled), now=NOW) == "MISSING-EVIDENCE", garbled


def test_missing_evidence_future_timestamp_failclosed():
    # a stamp AHEAD of now (negative age — clock skew / NTP) is unverifiable; fail closed,
    # never slip through as FRESH.
    assert bem.freshness_verdict(_report_aged(-3), now=NOW) == "MISSING-EVIDENCE"


# ── structural wiring ───────────────────────────────────────────────────────
def test_session_curation_in_display_dims():
    assert "session_curation" in bem.BASE_DISPLAY_DIMS
    assert "session_curation" in bem.DISPLAY_DIMS


def test_curated_fresh_is_ok_verdict():
    assert "CURATED-FRESH" in bem.OK_VERDICTS


def test_curation_group_exists_and_holds_session_curation():
    group = next((g for g in bem.GROUPS if g[0] == "curation"), None)
    assert group is not None, "GROUPS missing ('curation', ...) entry"
    assert group[2] == ["session_curation"]


def test_rollup_severity_ordering():
    sev = bem.ROLLUP_SEVERITY
    assert sev["CURATED-EXPIRED"] > sev["CURATED-STALE"] > sev["CURATED-FRESH"]
    assert sev["CURATED-FRESH"] == 0


def test_verdict_for_session_curation_grades_against_real_now():
    # the orchestrator routes the session_curation dim through freshness_verdict (graded vs
    # real now, not peers) — an expired stamp yields CURATED-EXPIRED for that cell.
    roster = {"dev-primary": {"status": "active"}}
    prov = {"checkout_sha": "abc1234", "dirty": False, "behind_main": 0, "ahead_main": 0,
            "origin_ref_age_h": 1}
    rep = {"machine": "dev-primary", "status": "active", "provenance": prov,
           "dimensions": {"session_curation": {
               "last_curated_at": (datetime.now() - timedelta(hours=100)).isoformat()}}}
    reports = {"dev-primary": rep}
    assert bem.verdict_for("session_curation", "dev-primary", reports, {},
                           roster, ["digitalmodel"]) == "CURATED-EXPIRED"
