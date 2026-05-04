"""Tests for review-open-issues.py — WRK-1336."""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent dir so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import importlib

roi = importlib.import_module("review-open-issues")


# ── Fixtures ──────────────────────────────────────────────────────────


SAMPLE_ISSUES = [
    {"number": 24, "title": "WRK-046: OrcaFlex drilling riser analysis",
     "labels": [{"name": "enhancement"}, {"name": "priority:medium"},
                {"name": "cat:engineering"}]},
    {"number": 25, "title": "WRK-047: OpenFOAM CFD analysis",
     "labels": [{"name": "enhancement"}, {"name": "priority:low"},
                {"name": "cat:engineering"}]},
    {"number": 31, "title": "WRK-1001: Workspace cleanup",
     "labels": [{"name": "priority:medium"}, {"name": "cat:harness"}]},
    {"number": 40, "title": "WRK-1050: Random task",
     "labels": [{"name": "enhancement"}]},
    {"number": 42, "title": "WRK-1060: High priority item",
     "labels": [{"name": "priority:high"}, {"name": "cat:engineering"}]},
]


# ── Tests ─────────────────────────────────────────────────────────────


def test_group_by_category():
    """Groups issues by cat:* label."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    assert "engineering" in groups
    assert "harness" in groups
    assert groups["engineering"]["count"] == 3
    assert groups["harness"]["count"] == 1
    assert len(groups["engineering"]["issues"]) == 3


def test_uncategorized_fallback():
    """Issues without cat:* go to uncategorized."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    assert "uncategorized" in groups
    assert groups["uncategorized"]["count"] == 1
    assert groups["uncategorized"]["issues"][0]["number"] == 40


def test_table_format():
    """Table output is readable and contains expected structure."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    output = roi.format_table(groups, total=len(SAMPLE_ISSUES))
    assert "Category: engineering (3 issues)" in output
    assert "#24" in output
    assert "#31" in output
    assert "Summary:" in output
    assert "5 open issues" in output


def test_yaml_format():
    """YAML output is valid and contains expected keys."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="category")
    output = roi.format_yaml(groups, total=len(SAMPLE_ISSUES))
    # Should be valid YAML (parse as dict via json since structure
    # is also valid JSON when formatted that way, or just check keys)
    assert "generated_at:" in output
    assert "total_open: 5" in output
    assert "engineering:" in output
    assert "count: 3" in output


def test_group_by_priority():
    """Groups by priority:* label."""
    groups = roi.group_issues(SAMPLE_ISSUES, group_by="priority")
    assert "medium" in groups
    assert "low" in groups
    assert "high" in groups
    assert groups["medium"]["count"] == 2
    assert groups["high"]["count"] == 1
    # Issues without priority:* label go to "unset"
    assert "unset" in groups


def test_empty_issues():
    """Handles no open issues gracefully."""
    groups = roi.group_issues([], group_by="category")
    assert groups == {}
    output = roi.format_table(groups, total=0)
    assert "0 open issues" in output


def test_flags_stale_artifact_when_issue_closed_after_generation(tmp_path):
    artifact = tmp_path / "results" / "2050.md"
    artifact.parent.mkdir()
    artifact.write_text(
        "Analysis for #2050\n\nRecommended next action: close this issue.\n",
        encoding="utf-8",
    )
    issues = [{"number": 2050, "title": "Done work", "state": "CLOSED"}]

    findings = roi.audit_issue_hygiene(issues, artifact_paths=[artifact])

    assert findings[0]["category"] == "stale-artifact"
    assert findings[0]["recommendation"] == "refresh"
    assert findings[0]["issues"] == [2050]


def test_flags_parent_child_drift_for_umbrella_with_closed_child(tmp_path):
    artifact = tmp_path / "1899.md"
    artifact.write_text(
        "Parent #1899 still routes work through child #2056.\n"
        "Recommended next action: continue via child issue.\n",
        encoding="utf-8",
    )
    issues = [
        {"number": 1899, "title": "Umbrella", "state": "OPEN"},
        {"number": 2056, "title": "Child", "state": "CLOSED"},
    ]

    findings = roi.audit_issue_hygiene(issues, artifact_paths=[artifact])

    assert any(
        f["category"] == "parent-child-drift"
        and f["recommendation"] == "verify"
        and f["issues"] == [1899, 2056]
        for f in findings
    )


def test_flags_repo_reality_contradiction_for_cited_changed_path(tmp_path):
    repo_root = tmp_path / "repo"
    real_path = repo_root / ".claude" / "skills" / "workspace-hub" / "session-start-routine"
    real_path.mkdir(parents=True)
    artifact = tmp_path / "1839.md"
    artifact.write_text(
        "Repo reality claim: missing path "
        "`.claude/skills/workspace-hub/session-start-routine`.\n",
        encoding="utf-8",
    )

    findings = roi.audit_issue_hygiene(
        [{"number": 1839, "title": "Skill audit", "state": "OPEN"}],
        artifact_paths=[artifact],
        repo_root=repo_root,
    )

    assert any(
        f["category"] == "repo-reality-contradiction"
        and f["recommendation"] == "verify"
        for f in findings
    )


def test_flags_stale_issue_premise_from_overlap_audit():
    issues = [{"number": 53, "title": "Old premise", "state": "OPEN"}]
    overlap = "#53 no longer matches repo reality; recommend close/defer."

    findings = roi.audit_issue_hygiene(issues, overlap_audit_text=overlap)

    assert any(
        f["category"] == "stale-premise"
        and f["recommendation"] == "verify"
        and f["issues"] == [53]
        for f in findings
    )


def test_requires_structural_signal_for_duplicate_detection():
    issues = [
        {"number": 100, "title": "Plan approval gate fix", "state": "OPEN"},
        {"number": 101, "title": "Fix plan approval gate", "state": "OPEN"},
    ]

    findings = roi.audit_issue_hygiene(issues)

    assert not [f for f in findings if f["category"] == "duplicate"]


def test_detects_duplicate_cluster_with_structural_evidence():
    issues = [
        {"number": 100, "title": "Plan approval gate fix", "state": "OPEN"},
        {"number": 101, "title": "Fix plan approval gate", "state": "OPEN"},
    ]
    overlap = "Duplicate / overlap cluster: #100 and #101 target same gate."

    findings = roi.audit_issue_hygiene(issues, overlap_audit_text=overlap)

    assert any(
        f["category"] == "duplicate"
        and f["recommendation"] == "merge"
        and f["issues"] == [100, 101]
        for f in findings
    )


def test_emits_stable_machine_readable_schema():
    finding = {
        "category": "duplicate",
        "recommendation": "merge",
        "confidence": "medium",
        "issues": [101, 100],
        "artifact": None,
        "evidence": "Duplicate / overlap cluster: #100 and #101",
    }

    output = json.loads(roi.format_hygiene_json([finding], generated_at="fixed"))

    assert output == {
        "generated_at": "fixed",
        "schema_version": 1,
        "finding_count": 1,
        "findings": [
            {
                "category": "duplicate",
                "recommendation": "merge",
                "confidence": "medium",
                "issues": [100, 101],
                "artifact": None,
                "evidence": "Duplicate / overlap cluster: #100 and #101",
            }
        ],
    }


def test_operator_report_groups_findings_by_action_bucket():
    findings = [
        {
            "category": "duplicate",
            "recommendation": "merge",
            "confidence": "medium",
            "issues": [100, 101],
            "artifact": None,
            "evidence": "duplicate cluster",
        },
        {
            "category": "stale-artifact",
            "recommendation": "refresh",
            "confidence": "high",
            "issues": [2050],
            "artifact": "results/2050.md",
            "evidence": "closed issue",
        },
    ]

    output = roi.format_hygiene_markdown(findings, generated_at="fixed")

    assert "## Refresh" in output
    assert "## Merge" in output
    assert "#2050" in output
    assert "#100, #101" in output


def test_weekly_review_reference_points_to_hygiene_audit():
    doc = Path("docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md")
    text = doc.read_text(encoding="utf-8")

    assert "review-open-issues.py --audit" in text
