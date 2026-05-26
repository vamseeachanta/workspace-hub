#!/usr/bin/env python3
"""Completeness score for issue closure — #2798.

Computes a 0-100 completeness score for a GitHub issue, reviewable before
`gh issue close`. Two classes, auto-derived from changed files (NOT selectable,
to close the "dodge code scoring via the ops path" gaming vector):

- ``code``     — test-derived: reuses the module-status-matrix (#1629)
                 ``quality_score`` + ``test_source_ratio`` per package, gated by a
                 changed-code coverage factor and an evidence-linked acceptance
                 checklist. Threshold 90.
- ``evidence`` — ops/docs/governance with no test surface: weighted ratio of met
                 evidence items (live-probe rubric per the prototype). Threshold 80.

This module is pure (no network / no I/O) so it is unit-testable under
pytest-socket; the CLI wrapper gathers changed files, the matrix snapshot, and
coverage from the environment and calls these functions.

Design corrections from #2798 plan review (Claude r1 + Codex r2):
- fail-closed on stale / missing matrix snapshot (snapshot SHA must match HEAD);
- multi-package scores take the conservative ``min``;
- checklist items without linked evidence do not count;
- ``test_source_ratio`` floor prevents low-value-test inflation.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

THRESHOLDS = {"code": 90, "evidence": 80}
TSR_FLOOR = 0.5            # below this, the package score is penalised
COVERAGE_FLOOR = 0.8       # changed-code coverage at/above this = no penalty
CHECKLIST_FLOOR = 0.8      # evidence-linked checklist ratio at/above this = no penalty
# code-score component weights are folded into the multiplicative-factor model below.


class CompletenessError(Exception):
    """Base for fail-closed completeness errors."""


class StaleSnapshotError(CompletenessError):
    """The module-status-matrix snapshot is not bound to the current HEAD."""


class MissingPackageError(CompletenessError):
    """A scored package is absent from the matrix snapshot."""


@dataclass
class CompletenessResult:
    pct: int
    cls: str
    threshold: int
    snapshot_sha: str | None
    evidence: list[str] = field(default_factory=list)
    issue_number: int | None = None          # binds the record to its issue (gate checks this)
    generated_at: str = field(default_factory=lambda: _dt.datetime.now(_dt.timezone.utc).isoformat())

    @property
    def passed(self) -> bool:
        return self.pct >= self.threshold

    def to_dict(self) -> dict:
        return {
            "completeness_pct": self.pct,
            "cls": self.cls,
            "threshold": self.threshold,   # advisory only — the gate uses server-side config, not this
            "passed": self.passed,
            "snapshot_sha": self.snapshot_sha,
            "issue_number": self.issue_number,
            "generated_at": self.generated_at,
            "evidence": list(self.evidence),
        }


def _factor(value: float, floor: float) -> float:
    """1.0 when value >= floor, else a linear penalty toward 0."""
    if floor <= 0:
        return 1.0
    return 1.0 if value >= floor else max(0.0, value / floor)


def classify(changed_files: list[str], path_package_map: dict[str, str]) -> str:
    """``code`` if any changed file maps to a package, else ``evidence``.

    Auto-derived and non-selectable: a cross-cutting change cannot opt out of
    code scoring by declaring itself ops.
    """
    for f in changed_files or []:
        for prefix in path_package_map:
            # path-boundary match: "src/foo" must not match "src/foo2/x" (Codex#10)
            norm = prefix if prefix.endswith("/") else prefix + "/"
            if f == prefix or f.startswith(norm):
                return "code"
    return "evidence"


def score_code(
    packages: list[str],
    snapshot: dict,
    head_sha: str,
    changed_code_coverage: float,
    checklist: list[dict],
    issue_number: int | None = None,
) -> CompletenessResult:
    """Score a code issue against the #1629 matrix snapshot.

    ``snapshot`` = ``{"sha": <commit>, "packages": {pkg: {"quality_score": int,
    "test_source_ratio": float}}}``. Fails closed if the snapshot is not bound to
    ``head_sha`` or a scored package is missing.
    """
    # validate coverage input — reject NaN/out-of-range instead of papering over (Codex#9)
    cov = float(changed_code_coverage)
    if not (0.0 <= cov <= 1.0):   # NaN compares False on both sides -> rejected
        raise CompletenessError(f"changed_code_coverage {changed_code_coverage!r} not in [0,1] (fail-closed)")
    changed_code_coverage = cov
    snap_sha = snapshot.get("sha")
    if snap_sha != head_sha:
        raise StaleSnapshotError(
            f"matrix snapshot sha {snap_sha!r} != HEAD {head_sha!r}; refusing to score (fail-closed)"
        )
    pkg_data = snapshot.get("packages", {})
    evidence: list[str] = []
    per_pkg_scores: list[float] = []
    for pkg in packages:
        if pkg not in pkg_data:
            raise MissingPackageError(f"package {pkg!r} absent from matrix snapshot (fail-closed)")
        q = float(pkg_data[pkg].get("quality_score", 0))
        tsr = float(pkg_data[pkg].get("test_source_ratio", 0.0))
        contrib = q * _factor(tsr, TSR_FLOOR)
        per_pkg_scores.append(contrib)
        evidence.append(f"{pkg}: quality_score={q:g} test_source_ratio={tsr:g} -> {contrib:g}")

    base = min(per_pkg_scores) if per_pkg_scores else 0.0

    # evidence-linked checklist: only items with linked evidence count
    if checklist:
        met = sum(1 for c in checklist if c.get("evidence"))
        checklist_ratio = met / len(checklist)
        evidence.append(f"checklist: {met}/{len(checklist)} items evidence-linked")
    else:
        # NO acceptance checklist = NO acceptance evidence -> penalise (Codex#8).
        # Code work should not pass at threshold without acceptance criteria.
        checklist_ratio = 0.0
        evidence.append("checklist: ABSENT — no acceptance evidence (penalised)")

    cov_factor = _factor(changed_code_coverage, COVERAGE_FLOOR)
    chk_factor = _factor(checklist_ratio, CHECKLIST_FLOOR)
    evidence.append(f"changed_code_coverage={changed_code_coverage:g} (factor {cov_factor:g})")

    pct = int(round(base * cov_factor * chk_factor))
    pct = max(0, min(100, pct))
    return CompletenessResult(pct=pct, cls="code", threshold=THRESHOLDS["code"],
                              snapshot_sha=snap_sha, evidence=evidence, issue_number=issue_number)


def score_evidence(items: list[dict], issue_number: int | None = None) -> CompletenessResult:
    """Score an ops/docs/governance issue as a weighted ratio of met evidence.

    ``items`` = ``[{"label": str, "weight": number, "met": bool}, ...]``.
    """
    if not items:
        raise CompletenessError("evidence scoring requires at least one evidence item (fail-closed)")
    weights = [float(i.get("weight", 1)) for i in items]
    if any(w < 0 for w in weights):                       # negative weights game the denominator (Codex#7)
        raise CompletenessError("evidence weights must be non-negative (fail-closed)")
    total = sum(weights)
    if total <= 0:
        raise CompletenessError("evidence weights sum to zero — cannot score (fail-closed)")
    met = sum(w for w, i in zip(weights, items) if i.get("met"))
    pct = max(0, min(100, int(round(met / total * 100))))
    evidence = [f"{i.get('label', '?')}: {'met' if i.get('met') else 'UNMET'} (w={i.get('weight', 1)})"
                for i in items]
    return CompletenessResult(pct=pct, cls="evidence", threshold=THRESHOLDS["evidence"],
                              snapshot_sha=None, evidence=evidence, issue_number=issue_number)
