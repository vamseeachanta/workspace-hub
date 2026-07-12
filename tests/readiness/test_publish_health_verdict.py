"""TDD tests for #3502 — publish_health matrix verdict (follow-on to #3500).

Targets build_equality_matrix.publish_health_verdict: PUBLISH-GATED when the last
equivalence publish failed or took gate-length time (>60s — the #3500 pre-push
RUN_ALL deadlock signature); PUBLISH-STALE when the last publish is older than the
daily-cron window; PUBLISH-OK otherwise; fail-closed MISSING-EVIDENCE on
missing/garbled facts (a box that NEVER published has no record at all).
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

NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def _rep(**ph) -> dict:
    base = {"last_publish_at": "2026-07-13T11:00:00Z",
            "last_publish_duration_s": 2, "last_publish_rc": 0}
    base.update(ph)
    return {"dimensions": {"publish_health": base}}


def test_ok_fresh_fast_publish():
    assert bem.publish_health_verdict(_rep(), now=NOW) == "PUBLISH-OK"


def test_gated_on_gate_length_duration():
    assert bem.publish_health_verdict(
        _rep(last_publish_duration_s=3720), now=NOW) == "PUBLISH-GATED"


def test_gated_on_nonzero_rc():
    assert bem.publish_health_verdict(
        _rep(last_publish_rc=3), now=NOW) == "PUBLISH-GATED"


def test_gated_dominates_stale():
    assert bem.publish_health_verdict(
        _rep(last_publish_at="2026-07-10T00:00:00Z", last_publish_duration_s=900),
        now=NOW) == "PUBLISH-GATED"


def test_stale_when_older_than_daily_window():
    assert bem.publish_health_verdict(
        _rep(last_publish_at="2026-07-12T00:00:00Z"), now=NOW) == "PUBLISH-STALE"


def test_missing_evidence_without_dimension():
    assert bem.publish_health_verdict({"dimensions": {}}, now=NOW) == "MISSING-EVIDENCE"


def test_missing_evidence_on_never_published_sentinel_value():
    assert bem.publish_health_verdict(
        _rep(last_publish_at="missing"), now=NOW) == "MISSING-EVIDENCE"


def test_missing_evidence_on_future_stamp():
    assert bem.publish_health_verdict(
        _rep(last_publish_at="2026-07-14T00:00:00Z"), now=NOW) == "MISSING-EVIDENCE"


def test_dim_registered_in_display_and_groups():
    assert "publish_health" in bem.BASE_DISPLAY_DIMS
    assert any("publish_health" in dims for _, _, dims in bem.GROUPS)
    assert bem.ROLLUP_SEVERITY["PUBLISH-GATED"] == 6
    assert bem.ROLLUP_SEVERITY["PUBLISH-STALE"] == 5
    assert bem.ROLLUP_SEVERITY["PUBLISH-OK"] == 0
    assert "PUBLISH-OK" in bem.OK_VERDICTS


def test_remediation_for_gated_names_the_deadlock():
    action, owner, by_design = bem.remediate("publish_health", "PUBLISH-GATED")
    assert "3500" in action and by_design is False
