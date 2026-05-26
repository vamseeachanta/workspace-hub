"""Tests for the #2798 completeness score module.

Pure-function contract (no network — pytest-socket safe). The module computes a
0-100 completeness score for an issue from data passed in (changed files, a
module-status-matrix snapshot, evidence items) — the CLI wrapper gathers that
data separately.
"""
import sys
from pathlib import Path

import pytest

# scripts/workflow is not a package; import the module by path.
SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import completeness_score as cs  # noqa: E402


# ---- classification: code vs evidence (auto, non-selectable) ----

def test_classify_code_when_changed_files_map_to_a_package():
    pkg_map = {"src/digitalmodel/": "digitalmodel"}
    assert cs.classify(["src/digitalmodel/orcaflex/mooring.py"], pkg_map) == "code"


def test_classify_evidence_when_no_changed_file_maps_to_a_package():
    pkg_map = {"src/digitalmodel/": "digitalmodel"}
    assert cs.classify(["docs/governance/policy.md", ".claude/rules/x.md"], pkg_map) == "evidence"


def test_classify_evidence_when_no_changed_files():
    assert cs.classify([], {"src/x/": "x"}) == "evidence"


# ---- code scoring: reuse #1629 quality_score + test_source_ratio ----

def _snapshot(sha="HEADSHA", **pkgs):
    return {"sha": sha, "packages": pkgs}


def test_score_code_combines_quality_coverage_checklist():
    snap = _snapshot(digitalmodel={"quality_score": 100, "test_source_ratio": 1.0})
    r = cs.score_code(
        packages=["digitalmodel"],
        snapshot=snap,
        head_sha="HEADSHA",
        changed_code_coverage=1.0,
        checklist=[{"text": "AC1", "evidence": True}, {"text": "AC2", "evidence": True}],
    )
    assert r.cls == "code"
    assert r.pct == 100
    assert r.passed is True
    assert r.threshold == 90


def test_score_code_multipackage_takes_min():
    snap = _snapshot(
        a={"quality_score": 100, "test_source_ratio": 1.0},
        b={"quality_score": 40, "test_source_ratio": 0.4},
    )
    r = cs.score_code(["a", "b"], snap, "HEADSHA", changed_code_coverage=1.0,
                      checklist=[{"text": "x", "evidence": True}])
    # min of the two package contributions dominates -> not 100
    assert r.pct < 100
    assert r.passed is False  # b drags below 90


def test_score_code_boundary_89_fails_90_passes():
    # construct inputs that land exactly on 90 vs 89
    snap90 = _snapshot(p={"quality_score": 90, "test_source_ratio": 1.0})
    r90 = cs.score_code(["p"], snap90, "HEADSHA", changed_code_coverage=0.9,
                        checklist=[{"text": "a", "evidence": True}])
    snap89 = _snapshot(p={"quality_score": 88, "test_source_ratio": 1.0})
    r89 = cs.score_code(["p"], snap89, "HEADSHA", changed_code_coverage=0.9,
                        checklist=[{"text": "a", "evidence": True}])
    assert r90.passed is True
    assert r89.passed is False


def test_score_code_checklist_without_evidence_does_not_count():
    snap = _snapshot(p={"quality_score": 100, "test_source_ratio": 1.0})
    r = cs.score_code(["p"], snap, "HEADSHA", changed_code_coverage=1.0,
                      checklist=[{"text": "claimed but unproven", "evidence": False}])
    # unproven checklist item drags the checklist component down
    assert r.pct < 100


# ---- fail-closed on stale / missing snapshot (Codex #8) ----

def test_score_code_stale_snapshot_fails_closed():
    snap = _snapshot(sha="OLDSHA", p={"quality_score": 100, "test_source_ratio": 1.0})
    with pytest.raises(cs.StaleSnapshotError):
        cs.score_code(["p"], snap, head_sha="HEADSHA", changed_code_coverage=1.0, checklist=[])


def test_score_code_missing_package_fails_closed():
    snap = _snapshot(p={"quality_score": 100, "test_source_ratio": 1.0})
    with pytest.raises(cs.MissingPackageError):
        cs.score_code(["not_in_snapshot"], snap, "HEADSHA", changed_code_coverage=1.0, checklist=[])


# ---- evidence scoring (ops/docs/governance: no test surface) ----

def test_score_evidence_weighted_ratio():
    items = [
        {"label": "live probe A", "weight": 2, "met": True},
        {"label": "live probe B", "weight": 1, "met": True},
        {"label": "live probe C", "weight": 1, "met": False},
    ]
    r = cs.score_evidence(items)
    assert r.cls == "evidence"
    assert r.pct == 75  # (2+1)/(2+1+1) = 75%
    assert r.threshold == 80
    assert r.passed is False


def test_score_evidence_all_met_is_100():
    r = cs.score_evidence([{"label": "x", "weight": 1, "met": True}])
    assert r.pct == 100 and r.passed is True


# ---- result is JSON-serializable for kanban --metadata persistence ----

def test_result_to_dict_is_json_safe():
    import json
    r = cs.score_evidence([{"label": "x", "weight": 1, "met": True}], issue_number=2798)
    d = r.to_dict()
    json.dumps(d)  # must not raise
    assert d["completeness_pct"] == 100
    assert d["cls"] == "evidence"
    assert d["issue_number"] == 2798
    assert "generated_at" in d and "evidence" in d


# ---- hardening guards (code review fixes) ----

def test_classify_prefix_boundary_no_false_match():
    # "src/foo2/x" must NOT match package prefix "src/foo"
    assert cs.classify(["src/foo2/x.py"], {"src/foo": "foo"}) == "evidence"
    assert cs.classify(["src/foo/x.py"], {"src/foo": "foo"}) == "code"


def test_score_code_rejects_out_of_range_coverage():
    snap = _snapshot(p={"quality_score": 100, "test_source_ratio": 1.0})
    with pytest.raises(cs.CompletenessError):
        cs.score_code(["p"], snap, "HEADSHA", changed_code_coverage=1.5,
                      checklist=[{"text": "a", "evidence": True}])


def test_score_code_rejects_nan_coverage():
    snap = _snapshot(p={"quality_score": 100, "test_source_ratio": 1.0})
    with pytest.raises(cs.CompletenessError):
        cs.score_code(["p"], snap, "HEADSHA", changed_code_coverage=float("nan"),
                      checklist=[{"text": "a", "evidence": True}])


def test_score_code_empty_checklist_does_not_pass():
    # no acceptance checklist -> heavy penalty -> not closure-eligible
    snap = _snapshot(p={"quality_score": 100, "test_source_ratio": 1.0})
    r = cs.score_code(["p"], snap, "HEADSHA", changed_code_coverage=1.0, checklist=[])
    assert r.passed is False


def test_score_evidence_rejects_negative_weight():
    with pytest.raises(cs.CompletenessError):
        cs.score_evidence([{"label": "x", "weight": -5, "met": False},
                           {"label": "y", "weight": 1, "met": True}])


def test_score_evidence_rejects_empty():
    with pytest.raises(cs.CompletenessError):
        cs.score_evidence([])
