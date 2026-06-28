#!/usr/bin/env python3
"""Evidence-threshold eligibility evaluator — #3296 (shadow-mode advisory only).

Implements the agents.md "Autonomous gate evolution" rule as a concrete
metric+threshold+eligibility policy. This module is a small, PURE, fail-closed,
SHADOW-MODE-ONLY advisory evaluator: it computes and records an eligibility
verdict, but it NEVER applies ``status:plan-approved`` (the human still applies
the label). True auto-apply is a separate, future, owner-authorized phase whose
hard precondition is amending the SOUL never-self-approve must-fire rule.

Design (mirrors ``scripts/workflow/completeness_score.py`` on three points, with
one deliberate divergence):

1. ``issue_class`` is DERIVED from changed files (+ labels), never caller-supplied
   (owner decision D5) — closes the "declare a load-bearing change eligible"
   gaming vector. ``evaluate_eligibility`` has no ``issue_class`` parameter.
2. Every raw metric is validated to be a finite real number in its DECLARED raw
   domain INSIDE ``normalize_metrics`` BEFORE any arithmetic (``1.0 - raw``,
   ``(raw - best)/span``), for BOTH higher-is-better and lower-is-better metrics,
   so a missing/None/non-finite/out-of-domain metric of ANY direction can never
   reach an arithmetic op and raise a ``TypeError``.
3. A small named threshold table.

Deliberate divergence from ``completeness_score.py``: that module RAISES on a
malformed metric (it is a scoring module whose only correct response to bad
input is to halt the score). This evaluator instead FAILS CLOSED to INELIGIBLE
(stays manual) on a missing, non-finite, or out-of-domain metric — the safe
state for a shadow-mode advisory gate is "keep the human-in-loop gate," so a
malformed metric yields the conservative *verdict*, not a raised exception a
shadow caller could swallow and mis-default.
"""
from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass, field

# ── Issue-class taxonomy ──────────────────────────────────────────────────
# Load-bearing classes are NEVER eligible, regardless of metrics.
INELIGIBLE_CLASSES = {
    "ci-workflow",
    "schema-contract",
    "security-legal",
    "outward-facing",
    "engineering-calc",
    "harness-enforcement",
    "gate-self-modification",
}
ELIGIBLE_CLASSES = {
    "docs-typo-index",     # single-file docs / index / README typo
    "test-only-additive",  # pure additive test changes, no src
    "low-risk-config",     # non-CI, non-schema config edits
}

# ── Metric direction vocabulary ───────────────────────────────────────────
DIRECTION_HIGHER = "higher_is_better"
DIRECTION_RATE_LOWER = "rate_lower_better"
DIRECTION_COUNT_LOWER = "count_lower_better"


@dataclass
class MetricSpec:
    """Declares a metric's normalization direction + raw domain ``[raw_lo, raw_hi]``.

    ``higher_is_better`` / ``rate_lower_better`` -> raw domain [0.0, 1.0].
    ``count_lower_better`` -> raw domain [best, best + span].
    """

    direction: str
    best: float = 0.0
    span: float = 1.0
    raw_lo: float = field(init=False)
    raw_hi: float = field(init=False)

    def __post_init__(self) -> None:
        if self.direction in (DIRECTION_HIGHER, DIRECTION_RATE_LOWER):
            self.raw_lo, self.raw_hi = 0.0, 1.0
        elif self.direction == DIRECTION_COUNT_LOWER:
            if self.span <= 0:
                raise ValueError("count_lower_better span must be > 0")
            self.raw_lo, self.raw_hi = float(self.best), float(self.best) + float(self.span)
        else:
            raise ValueError(f"unknown metric direction {self.direction!r}")


@dataclass
class EligibilityConfig:
    metric_specs: dict[str, MetricSpec]
    thresholds: dict[str, float]
    min_sample: int = 20
    kill_switch_on: bool = False


@dataclass
class Verdict:
    """An eligibility verdict. ``mode`` is only ever ``"shadow"`` or ``"manual"``;
    there is NO ``auto_apply`` mode — the evaluator never self-approves."""

    eligible: bool
    mode: str
    reason: str
    issue_class: str | None = None
    audit: dict | None = None


# ── Default policy (owner decides final numbers at approval) ───────────────
def default_metric_specs() -> dict[str, MetricSpec]:
    return {
        "adversarial_review_approve_rate": MetricSpec(DIRECTION_HIGHER),
        "post_merge_revert_rate": MetricSpec(DIRECTION_RATE_LOWER),
        "completeness_gate_pass_rate": MetricSpec(DIRECTION_HIGHER),
        "reproduction_compliance_rate": MetricSpec(DIRECTION_HIGHER),
        "plan_revision_rounds": MetricSpec(DIRECTION_COUNT_LOWER, best=1.0, span=4.0),
    }


def default_thresholds() -> dict[str, float]:
    # normalized (higher-is-better [0,1]) thresholds
    return {
        "adversarial_review_approve_rate": 0.90,
        "post_merge_revert_rate": 0.95,        # normalized 1 - rate
        "completeness_gate_pass_rate": 0.90,
        "reproduction_compliance_rate": 0.90,
        "plan_revision_rounds": 0.50,          # normalized
    }


def default_config() -> EligibilityConfig:
    return EligibilityConfig(
        metric_specs=default_metric_specs(),
        thresholds=default_thresholds(),
        min_sample=20,
        kill_switch_on=False,
    )


# ── Helpers ───────────────────────────────────────────────────────────────
def _is_finite_number(x) -> bool:
    """True only for a real, finite int/float. Rejects None, bool, str, NaN, Inf."""
    if isinstance(x, bool):           # bool is an int subclass — reject explicitly
        return False
    if not isinstance(x, (int, float)):
        return False
    return math.isfinite(x)


def _ineligible(reason: str, issue_class: str | None = None) -> Verdict:
    return Verdict(eligible=False, mode="manual", reason=reason, issue_class=issue_class)


def _eligible_shadow(reason: str, issue_class: str, audit: dict) -> Verdict:
    return Verdict(eligible=True, mode="shadow", reason=reason, issue_class=issue_class, audit=audit)


# ── Deterministic classifier (D5: derived, never caller-supplied) ─────────
def _load_bearing_class_for_file(f: str) -> str | None:
    """Return the load-bearing class for a single changed file, or None.

    Ordered so the highest-priority load-bearing signal wins. A cross-cutting
    change can therefore never down-classify itself into an eligible bucket.
    """
    # CI / workflow
    if f.startswith(".github/workflows/") or f.startswith(".github/actions/"):
        return "ci-workflow"
    # schema / contract / registry
    if f.startswith("schema/") or "/schema/" in f or f.endswith(".schema.json") or "registry" in f:
        return "schema-contract"
    # security / legal / secrets
    if (
        f.startswith(".legal-")
        or f.startswith("scripts/legal/")
        or "/legal/" in f
        or "secret" in f.lower()
    ):
        return "security-legal"
    # gate / hook self-modification
    if f.startswith(".claude/hooks/") or "plan-approval-gate" in f:
        return "gate-self-modification"
    # harness / enforcement / agent identity
    if (
        f.startswith("scripts/enforcement/")
        or "SOUL" in f
        or f.endswith("agents.md")
        or f.endswith("AGENTS.md")
        or f.startswith("config/agents/")
    ):
        return "harness-enforcement"
    # engineering calc (source packages) — over-broad on purpose (fail-safe: stays manual)
    if f.startswith("src/") or "/src/" in f or f.startswith("packages/"):
        return "engineering-calc"
    # outward-facing (client-shared reports / public sites)
    if "client" in f.lower() or "/public/" in f or f.startswith("public/") or "/sites/" in f:
        return "outward-facing"
    return None


def _is_doc_file(f: str) -> bool:
    base = f.rsplit("/", 1)[-1].lower()
    return (
        f.endswith(".md")
        or f.endswith(".rst")
        or f.startswith("docs/")
        or "/docs/" in f
        or base.startswith("readme")
        or base.startswith("index")
    )


def _is_test_file(f: str) -> bool:
    return f.startswith("tests/") or "/tests/" in f or f.startswith("test/")


def _is_low_risk_config_file(f: str) -> bool:
    return f.endswith((".yml", ".yaml", ".json", ".toml", ".ini", ".cfg"))


def _label_load_bearing_class(labels) -> str | None:
    for l in labels or []:
        ls = str(l)
        if ls.startswith("gate:"):
            return "harness-enforcement"
        if ls.startswith("client:"):
            return "outward-facing"
    return None


def classify(changed_files, labels) -> str:
    """Deterministically derive the issue class from changed files + labels.

    Load-bearing signals win (checked first, in priority order). Only when NO
    changed file and NO label carries a load-bearing signal does the change fall
    into an eligible bucket (all-docs / all-tests / all-low-risk-config), else
    ``"unknown"`` (fail-closed to manual downstream).
    """
    files = list(changed_files or [])

    # 1. First load-bearing file wins.
    for f in files:
        cls = _load_bearing_class_for_file(f)
        if cls is not None:
            return cls

    # 2. Load-bearing labels (authoritative issue state, read via gh — not agent-asserted).
    label_cls = _label_load_bearing_class(labels)
    if label_cls is not None:
        return label_cls

    if not files:
        return "unknown"

    # 3. Eligible buckets — require ALL files to satisfy the bucket predicate.
    if all(_is_doc_file(f) for f in files):
        return "docs-typo-index"
    if all(_is_test_file(f) for f in files):
        return "test-only-additive"
    if all(_is_low_risk_config_file(f) for f in files):
        return "low-risk-config"

    return "unknown"


# ── Metric normalization (validate BEFORE any arithmetic) ─────────────────
def normalize_metrics(raw_metrics, metric_specs):
    """Validate then normalize every metric to higher-is-better [0,1].

    Returns ``(normalized_dict, None)`` on success, else ``(None, bad_name)`` for
    the FIRST raw metric that is missing/None/non-numeric/NaN/Inf/out-of-domain.
    NEVER raises — the caller maps a non-None ``bad_name`` to INELIGIBLE.

    Validation runs BEFORE any arithmetic (``1.0 - raw``, ``(raw - best)/span``)
    for every direction, so a malformed lower-is-better/count metric fails closed
    instead of raising a ``TypeError`` inside the arithmetic.
    """
    normalized: dict[str, float] = {}
    for name, spec in metric_specs.items():
        raw = raw_metrics.get(name)
        if not _is_finite_number(raw) or not (spec.raw_lo <= raw <= spec.raw_hi):
            return (None, name)
        raw = float(raw)
        if spec.direction == DIRECTION_HIGHER:
            v = raw
        elif spec.direction == DIRECTION_RATE_LOWER:
            v = 1.0 - raw
        else:  # DIRECTION_COUNT_LOWER
            v = max(0.0, min(1.0, 1.0 - (raw - spec.best) / spec.span))
        normalized[name] = v
    return (normalized, None)


def build_ledger_record(issue_class, normalized, raw_metrics, config) -> dict:
    return {
        "reviewed_commit_sha": raw_metrics.get("reviewed_commit_sha"),
        "plan_path": raw_metrics.get("plan_path"),
        "review_artifact_paths": raw_metrics.get("review_artifact_paths", []),
        "issue_class": issue_class,
        "raw_metric_snapshot": {k: raw_metrics.get(k) for k in config.metric_specs},
        "normalized_metric_snapshot": dict(normalized),
        "thresholds": dict(config.thresholds),
        "window_bounds": raw_metrics.get("window_bounds"),
        "sample_size": raw_metrics.get("sample_size"),
        "decision": "ELIGIBLE_SHADOW",
        "decided_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mode": "shadow",
    }


def evaluate_eligibility(changed_files, labels, raw_metrics, config) -> Verdict:
    """Decide shadow-mode eligibility. NEVER raises; fails closed to INELIGIBLE.

    NOTE: there is no ``issue_class`` parameter — the class is DERIVED via
    ``classify()`` (D5), so a caller cannot declare a load-bearing change eligible.
    """
    if config.kill_switch_on:
        return _ineligible("kill-switch engaged — always manual")

    issue_class = classify(changed_files, labels)

    if issue_class in INELIGIBLE_CLASSES:
        return _ineligible(f"load-bearing class '{issue_class}' — stays manual", issue_class)
    if issue_class not in ELIGIBLE_CLASSES:
        return _ineligible(
            f"class '{issue_class}' not in eligible set — fail-closed to manual", issue_class
        )

    # sample-size gate (coerce defensively; non-int -> 0 -> insufficient)
    sample = raw_metrics.get("sample_size")
    if not isinstance(sample, int) or isinstance(sample, bool):
        sample = 0
    if sample < config.min_sample:
        return _ineligible(
            f"insufficient sample (n={sample} < {config.min_sample})", issue_class
        )

    # validate + normalize every metric BEFORE any arithmetic; fail closed on bad input
    normalized, bad_metric = normalize_metrics(raw_metrics, config.metric_specs)
    if bad_metric is not None:
        return _ineligible(
            f"metric '{bad_metric}' missing/non-finite/out-of-domain — fail-closed to manual",
            issue_class,
        )

    for metric, threshold in config.thresholds.items():
        value = normalized.get(metric)
        # defense-in-depth: normalized value must be a finite float in [0,1]
        if value is None or not _is_finite_number(value) or not (0.0 <= value <= 1.0):
            return _ineligible(
                f"metric '{metric}' normalized out-of-range ({value!r}) — fail-closed to manual",
                issue_class,
            )
        if value < threshold:
            return _ineligible(
                f"metric {metric}={value:.3f} < {threshold:.3f}", issue_class
            )

    audit = build_ledger_record(issue_class, normalized, raw_metrics, config)
    return _eligible_shadow(
        "all metrics pass; SHADOW MODE — human still applies label",
        issue_class,
        audit,
    )
