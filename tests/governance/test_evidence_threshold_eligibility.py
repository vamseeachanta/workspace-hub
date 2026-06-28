"""TDD suite for the #3296 evidence-threshold eligibility evaluator.

Pure-function contract (no network — pytest-socket safe). The evaluator derives
issue_class deterministically from changed files (never caller-supplied),
validates every raw metric BEFORE any normalization arithmetic, fails CLOSED to
INELIGIBLE on malformed input (never raises a TypeError), normalizes every metric
to higher-is-better [0,1] before the threshold loop, and only ever returns a
shadow-mode verdict (never auto-apply).
"""
import inspect
import math
import sys
from pathlib import Path

import pytest

# scripts/governance is not a package; import the module by path.
SCRIPTS_GOVERNANCE = Path(__file__).resolve().parents[2] / "scripts" / "governance"
sys.path.insert(0, str(SCRIPTS_GOVERNANCE))

import evidence_threshold_eligibility as ete  # noqa: E402


# ---- helpers -------------------------------------------------------------

def _passing_raw(**overrides):
    """A raw-metrics dict that passes the default config's thresholds."""
    raw = {
        "sample_size": 50,
        "adversarial_review_approve_rate": 0.95,
        "post_merge_revert_rate": 0.01,        # lower-is-better -> normalizes to 0.99
        "completeness_gate_pass_rate": 0.95,
        "reproduction_compliance_rate": 0.95,
        "plan_revision_rounds": 1.0,           # count-lower-better -> normalizes high
        "reviewed_commit_sha": "abc123",
        "plan_path": "docs/plans/2026-06-28-foo.md",
        "review_artifact_paths": ["scripts/review/results/x-claude.md"],
        "window_bounds": "2026-06-01..2026-06-28",
    }
    raw.update(overrides)
    return raw


def _config(**overrides):
    cfg = ete.default_config()
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


DOCS = ["docs/foo.md"]


# ---- classify: deterministic, load-bearing-first -------------------------

def test_classify_ci_workflow_changed_file():
    assert ete.classify([".github/workflows/x.yml"], []) == "ci-workflow"


def test_classify_gate_self_mod_changed_file():
    assert ete.classify([".claude/hooks/plan-approval-gate.sh"], []) == "gate-self-modification"


def test_classify_docs_typo_single_file():
    assert ete.classify(["docs/foo.md"], []) == "docs-typo-index"


def test_classify_mixed_change_picks_load_bearing():
    # a docs + CI change cannot down-classify to docs
    assert ete.classify(["docs/foo.md", ".github/workflows/x.yml"], []) == "ci-workflow"


def test_classify_unknown_when_no_rule_matches():
    assert ete.classify(["weird/path.bin"], []) == "unknown"


def test_issue_class_is_not_a_parameter():
    sig = inspect.signature(ete.evaluate_eligibility)
    assert "issue_class" not in sig.parameters


# ---- eligibility gating --------------------------------------------------

def test_load_bearing_class_blocked_even_with_perfect_metrics():
    v = ete.evaluate_eligibility([".github/workflows/x.yml"], [], _passing_raw(), _config())
    assert not v.eligible
    assert "ci-workflow" in v.reason


def test_unknown_class_fails_closed():
    v = ete.evaluate_eligibility(["weird/path.bin"], [], _passing_raw(), _config())
    assert not v.eligible
    assert "fail-closed" in v.reason


def test_kill_switch_forces_manual():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(), _config(kill_switch_on=True))
    assert not v.eligible
    assert "kill-switch" in v.reason


def test_insufficient_sample_blocks():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(sample_size=3), _config(min_sample=20))
    assert not v.eligible
    assert "sample" in v.reason


# ---- normalization is load-bearing ---------------------------------------

def test_lower_is_better_metric_normalized_before_loop():
    # post_merge_revert_rate raw=0.02 -> normalized 0.98 >= 0.95 threshold -> passes
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(post_merge_revert_rate=0.02), _config())
    assert v.eligible


def test_lower_is_better_metric_unnormalized_would_fail():
    # proves normalization is load-bearing: raw 0.02 compared RAW against 0.95
    # would block; the normalized path (1-0.02=0.98) passes.
    specs = ete.default_metric_specs()
    norm, bad = ete.normalize_metrics({"post_merge_revert_rate": 0.02}, {"post_merge_revert_rate": specs["post_merge_revert_rate"]})
    assert bad is None
    assert norm["post_merge_revert_rate"] == pytest.approx(0.98)


def test_metric_below_threshold_blocks():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(adversarial_review_approve_rate=0.7), _config())
    assert not v.eligible
    assert "adversarial_review_approve_rate" in v.reason


def test_eligible_shadow_when_all_pass():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(), _config())
    assert v.eligible
    assert v.mode == "shadow"
    assert v.audit is not None


# ---- ledger + shadow-only contract ---------------------------------------

def test_ledger_record_has_required_fields():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(), _config())
    rec = v.audit
    for key in (
        "reviewed_commit_sha", "plan_path", "review_artifact_paths", "issue_class",
        "raw_metric_snapshot", "normalized_metric_snapshot", "decided_at_utc",
    ):
        assert key in rec, f"ledger record missing {key}"
    assert rec["mode"] == "shadow"


def test_shadow_mode_never_returns_auto_apply():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(), _config())
    assert v.mode == "shadow"
    # no auto-apply path exists in the verdict vocabulary
    assert v.mode in {"shadow", "manual"}


# ---- fail-closed: higher-is-better malformed -----------------------------

def test_nan_metric_yields_ineligible():
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(adversarial_review_approve_rate=float("nan")), _config())
    assert not v.eligible
    assert "adversarial_review_approve_rate" in v.reason


def test_out_of_range_metric_yields_ineligible():
    for bad in (1.4, -0.1):
        v = ete.evaluate_eligibility(DOCS, [], _passing_raw(adversarial_review_approve_rate=bad), _config())
        assert not v.eligible
        assert "adversarial_review_approve_rate" in v.reason


# ---- fail-closed: lower-is-better malformed (before 1.0 - raw runs) -------

def test_missing_lower_is_better_metric_yields_ineligible():
    raw = _passing_raw()
    del raw["post_merge_revert_rate"]
    v = ete.evaluate_eligibility(DOCS, [], raw, _config())
    assert not v.eligible
    assert "post_merge_revert_rate" in v.reason


def test_nonfinite_lower_is_better_metric_yields_ineligible():
    for bad in (float("nan"), float("inf"), "x"):
        v = ete.evaluate_eligibility(DOCS, [], _passing_raw(post_merge_revert_rate=bad), _config())
        assert not v.eligible
        assert "post_merge_revert_rate" in v.reason


def test_missing_count_lower_better_metric_yields_ineligible():
    raw = _passing_raw()
    del raw["plan_revision_rounds"]
    v = ete.evaluate_eligibility(DOCS, [], raw, _config())
    assert not v.eligible
    assert "plan_revision_rounds" in v.reason


def test_normalize_metrics_returns_bad_name_not_raise():
    specs = ete.default_metric_specs()
    # one missing lower-is-better metric -> returns (None, name), never raises
    norm, bad = ete.normalize_metrics({"adversarial_review_approve_rate": 0.9}, specs)
    assert norm is None
    assert bad in specs  # the first bad metric name


def test_normalize_metrics_does_not_raise_on_nonnumeric_lower_is_better():
    specs = {"post_merge_revert_rate": ete.default_metric_specs()["post_merge_revert_rate"]}
    # must not raise a TypeError on `1.0 - "x"`
    norm, bad = ete.normalize_metrics({"post_merge_revert_rate": "x"}, specs)
    assert norm is None
    assert bad == "post_merge_revert_rate"


def test_bool_metric_rejected():
    # bool is an int subclass; must be rejected as non-numeric
    v = ete.evaluate_eligibility(DOCS, [], _passing_raw(adversarial_review_approve_rate=True), _config())
    assert not v.eligible
