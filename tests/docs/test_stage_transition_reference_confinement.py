from __future__ import annotations

import re
import subprocess
from fnmatch import fnmatch
from pathlib import Path

import pytest

from tests.helpers.stale_reference_docs import (
    REPO_ROOT,
    STAGE_TRANSITION_SCRIPT_PATHS,
    STAGE_TRANSITION_SCRIPT_PATTERNS,
    scan_stale_reference_hits,
)

PROTECTED_CURRENT_SURFACE_FILES: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "docs/README.md",
    "docs/context-pipeline.md",
    "docs/governance/TRUST-ARCHITECTURE.md",
    "docs/modules/workflow/SPEC_LOCALITY_POLICY.md",
    "docs/work-queue-workflow.md",
    "docs/plans/README.md",
    ".claude/docs/data-format-guide.md",
)

PROTECTED_CURRENT_SURFACE_GLOBS: tuple[str, ...] = (
    ".planning/templates/*.md",
    ".claude/docs/*.md",
    ".claude/commands/**/*.md",
    ".claude/skills/**/*.md",
    ".gemini/**/*.md",
)

ALLOWED_LEGACY_REDIRECT_FILES: frozenset[str] = frozenset(
    {
        "docs/ops/legacy-claude-reference-map.md",
        "docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md",
    }
)

TOOLING_RETAINED_REFERENCE_FILES: frozenset[str] = frozenset(
    {
        "tests/helpers/stale_reference_docs.py",
        "tests/docs/test_stage_transition_reference_confinement.py",
        "tests/analysis/test_provider_session_ecosystem_audit.py",
        "tests/session-analysis/test_stage_exit_signal.bats",
        "tests/work-queue/test_engine_integration.sh",
        "tests/work-queue/test_stage_lifecycle.py",
        "tests/work-queue/test_stderr_cleanup.py",
        "tests/work-queue/test_transition_hardening.py",
        "scripts/analysis/provider_session_ecosystem_audit.py",
    }
)

HISTORICAL_EVIDENCE_PATH_PREFIXES: tuple[str, ...] = (
    "docs/reports/",
    "analysis/",
    "scripts/review/results/",
    ".claude/state/corrections/",
    ".planning/quick/",
    ".planning/archive/",
    ".planning/skills/",
    "data/",
    "docs/plans/2026-04-01-knowledge-persistence-architecture.md",
    "logs/",
    "state/reflect-history/",
    "state/session-signals/",
    ".claude/state/session-signals/",
)

HISTORICAL_EVIDENCE_SUFFIXES: tuple[str, ...] = (".md", ".json", ".jsonl", ".csv", ".txt", ".out")

REQUIRED_REDIRECT_TARGETS: tuple[str, ...] = (
    "docs/governance/SESSION-GOVERNANCE.md",
    "docs/governance/TRUST-ARCHITECTURE.md",
    "scripts/workflow/governance-checkpoints.yaml",
    ".claude/hooks/plan-approval-gate.sh",
    ".claude/hooks/session-governor-check.sh",
    "scripts/review/cross-review.sh",
)

LEGACY_MAP_RELATIVE_PATH = "docs/ops/legacy-claude-reference-map.md"
AUDIT_RULE_RELATIVE_PATH = "scripts/analysis/provider_session_ecosystem_audit.py"
AUDIT_RULE_ID = "legacy_work_queue_transition"

PLAN_ALLOWED_HISTORY_EXTRA_FILES: frozenset[str] = frozenset(
    {
        "docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md",
    }
)


def _iter_protected_surface_paths() -> list[str]:
    """Expand the fixed protected-surface universe into concrete repo-relative paths."""
    paths: set[str] = set(PROTECTED_CURRENT_SURFACE_FILES)
    tracked_paths = subprocess.check_output(
        ["git", "ls-files"], cwd=REPO_ROOT, text=True
    ).splitlines()
    for glob in PROTECTED_CURRENT_SURFACE_GLOBS:
        paths.update(path for path in tracked_paths if fnmatch(path, glob))
    return sorted(paths)


def _classify_hit_path(relative_path: str) -> str:
    """Place a hit path into exactly one of: allowed, tooling, history, unexpected."""
    if relative_path in ALLOWED_LEGACY_REDIRECT_FILES:
        return "allowed"
    if relative_path in TOOLING_RETAINED_REFERENCE_FILES:
        return "tooling"
    if relative_path in PLAN_ALLOWED_HISTORY_EXTRA_FILES:
        return "history"
    for prefix in HISTORICAL_EVIDENCE_PATH_PREFIXES:
        if relative_path.startswith(prefix) and relative_path.endswith(HISTORICAL_EVIDENCE_SUFFIXES):
            return "history"
    return "unexpected"


def test_stage_transition_references_are_forbidden_in_protected_current_surfaces() -> None:
    """The fixed protected current-surface universe must stay clean of the three stage-transition script names."""
    violations: list[str] = []
    for relative_path in _iter_protected_surface_paths():
        hits = scan_stale_reference_hits(relative_path, patterns=STAGE_TRANSITION_SCRIPT_PATTERNS)
        violations.extend(hits)
    assert not violations, (
        "Protected current-surface files must not mention deleted stage-transition scripts:\n"
        + "\n".join(violations)
    )


def test_stage_transition_known_live_hit_removed_from_data_format_guide() -> None:
    """The known live hit in .claude/docs/data-format-guide.md must be gone and stay gone."""
    hits = scan_stale_reference_hits(
        ".claude/docs/data-format-guide.md",
        patterns=STAGE_TRANSITION_SCRIPT_PATTERNS,
    )
    assert not hits, (
        ".claude/docs/data-format-guide.md still mentions a deleted stage-transition script:\n"
        + "\n".join(hits)
    )


def _collect_stage_transition_hits_across_repo() -> dict[str, list[str]]:
    """Use git grep over tracked files and bucket stage-transition hits by classification."""
    buckets: dict[str, list[str]] = {"allowed": [], "tooling": [], "history": [], "unexpected": []}
    grep = subprocess.run(
        [
            "git",
            "grep",
            "-l",
            "-E",
            r"(scripts/work-queue/)?(start_stage|exit_stage|verify_checklist)\.py",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert grep.returncode in (0, 1), grep.stderr
    for relative_str in grep.stdout.splitlines():
        bucket = _classify_hit_path(relative_str)
        buckets[bucket].append(relative_str)
    for bucket in buckets.values():
        bucket.sort()
    return buckets


def test_stage_transition_references_are_limited_to_two_legacy_redirect_docs_outside_history_and_tooling_buckets() -> None:
    """Outside the history and tooling buckets, only the two enumerated legacy-redirect docs may retain the names."""
    buckets = _collect_stage_transition_hits_across_repo()
    assert not buckets["unexpected"], (
        "Stage-transition script mentions escaped the fixed bucket taxonomy:\n"
        + "\n".join(buckets["unexpected"])
    )
    allowed_hits = set(buckets["allowed"])
    assert allowed_hits.issubset(ALLOWED_LEGACY_REDIRECT_FILES), (
        "Allowed bucket contained files outside the enumerated legacy-redirect set:\n"
        + "\n".join(sorted(allowed_hits - ALLOWED_LEGACY_REDIRECT_FILES))
    )
    assert "docs/ops/legacy-claude-reference-map.md" in allowed_hits, (
        "Expected docs/ops/legacy-claude-reference-map.md to retain the legacy redirect entries for the three scripts"
    )


def test_stage_transition_tooling_sources_are_explicitly_classified_not_false_flagged() -> None:
    """Detector/remediation sources must land in the tooling bucket, not the unexpected bucket."""
    for tooling_path in TOOLING_RETAINED_REFERENCE_FILES:
        assert (REPO_ROOT / tooling_path).is_file(), (
            f"Tooling-bucket source is missing on disk: {tooling_path}"
        )
        assert _classify_hit_path(tooling_path) == "tooling", (
            f"Tooling-bucket source was misclassified: {tooling_path}"
        )

    buckets = _collect_stage_transition_hits_across_repo()
    tooling_actual = set(buckets["tooling"])
    assert AUDIT_RULE_RELATIVE_PATH in tooling_actual, (
        "scripts/analysis/provider_session_ecosystem_audit.py should still be the source of the canonical "
        "legacy_work_queue_transition mapping"
    )


def test_stage_transition_redirect_targets_exist_in_legacy_map_and_audit_rule() -> None:
    """Redirect guidance must be measurable: both repo-attested sources carry every required current target."""
    legacy_map_text = (REPO_ROOT / LEGACY_MAP_RELATIVE_PATH).read_text(encoding="utf-8")
    missing_from_legacy_map = [t for t in REQUIRED_REDIRECT_TARGETS if t not in legacy_map_text]
    assert not missing_from_legacy_map, (
        f"{LEGACY_MAP_RELATIVE_PATH} is missing required redirect targets:\n"
        + "\n".join(missing_from_legacy_map)
    )

    audit_text = (REPO_ROOT / AUDIT_RULE_RELATIVE_PATH).read_text(encoding="utf-8")
    assert AUDIT_RULE_ID in audit_text, (
        f"{AUDIT_RULE_RELATIVE_PATH} must still declare rule id {AUDIT_RULE_ID!r}"
    )
    rule_block = _extract_legacy_work_queue_transition_block(audit_text)
    missing_from_audit = [t for t in REQUIRED_REDIRECT_TARGETS if t not in rule_block]
    assert not missing_from_audit, (
        f"{AUDIT_RULE_RELATIVE_PATH} {AUDIT_RULE_ID!r} block is missing required canonical targets:\n"
        + "\n".join(missing_from_audit)
    )
    for script_path in STAGE_TRANSITION_SCRIPT_PATHS:
        assert script_path in rule_block, (
            f"{AUDIT_RULE_RELATIVE_PATH} {AUDIT_RULE_ID!r} block must list legacy path {script_path!r}"
        )


def _extract_legacy_work_queue_transition_block(audit_text: str) -> str:
    """Return the slice of the audit file spanning the legacy_work_queue_transition rule dict."""
    anchor = f'"rule_id": "{AUDIT_RULE_ID}"'
    start = audit_text.find(anchor)
    assert start != -1, f"Audit file missing anchor {anchor!r}"
    next_rule = audit_text.find('"rule_id":', start + len(anchor))
    end = next_rule if next_rule != -1 else len(audit_text)
    return audit_text[start:end]


def test_stage_transition_pattern_matches_sample_reintroduction() -> None:
    """Negative/mutation-style proof: a fabricated protected-surface reintroduction must match the guardrail."""
    sample_text = (
        "# Hypothetical reintroduction in a protected current surface\n"
        "Run `uv run python scripts/work-queue/start_stage.py WRK-9999 1` to open stage 1.\n"
    )
    sample_file = Path("/tmp/_stage_transition_reintroduction_sample.md")
    sample_file.write_text(sample_text, encoding="utf-8")
    try:
        compiled = [pattern for _, pattern in STAGE_TRANSITION_SCRIPT_PATTERNS]
        matches = [p.search(sample_text) for p in compiled]
        assert any(m is not None for m in matches), (
            "STAGE_TRANSITION_SCRIPT_PATTERNS failed to match a known-bad protected-surface reintroduction"
        )
    finally:
        sample_file.unlink(missing_ok=True)


def test_stage_transition_pattern_does_not_fire_on_unrelated_text() -> None:
    """Guardrail must not over-match text that only mentions similar words without the full deleted path."""
    safe_samples = [
        "The workflow uses .planning/ for evidence and scripts/review/cross-review.sh for review.",
        "See docs/governance/SESSION-GOVERNANCE.md for current stage transitions.",
        "start_stage as a concept is fine when it does not name the deleted script path",
    ]
    compiled = [pattern for _, pattern in STAGE_TRANSITION_SCRIPT_PATTERNS]
    for sample in safe_samples:
        for pattern in compiled:
            match = pattern.search(sample)
            assert match is None, (
                f"STAGE_TRANSITION_SCRIPT_PATTERNS matched unrelated safe sample: {sample!r} via {pattern.pattern!r}"
            )


def test_stage_transition_pattern_entries_are_pattern_objects() -> None:
    """Structural guard: the exported pattern list must stay compatible with scan_stale_reference_hits."""
    assert STAGE_TRANSITION_SCRIPT_PATTERNS, "STAGE_TRANSITION_SCRIPT_PATTERNS must not be empty"
    for label, pattern in STAGE_TRANSITION_SCRIPT_PATTERNS:
        assert isinstance(label, str) and label, "Pattern entry label must be a non-empty string"
        assert isinstance(pattern, re.Pattern), "Pattern entry value must be a compiled regex"
