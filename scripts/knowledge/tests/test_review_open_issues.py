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
        "Generated: 2026-04-10T09:00:00Z\n"
        "Analysis for #2050\n\nRecommended next action: close this issue.\n",
        encoding="utf-8",
        newline="\n",
    )
    # Synthetic chronology: closure follows generation by one hour.
    issues = [{"number": 2050, "title": "Done work", "state": "CLOSED",
               "closedAt": "2026-04-10T10:00:00Z"}]

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
        newline="\n",
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
        newline="\n",
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


# All examples below are synthetic. Issue numbers are arbitrary identifiers.
# Chronological expectations follow the displayed UTC instants by hand:
# 09:00Z < 10:00Z < 11:00Z; 11:00+02:00 = 09:00Z;
# 09:00-02:00 = 11:00Z. No filesystem timestamp supplies audit evidence.
CLOSED_EXAMPLE = {
    "number": 100, "state": "CLOSED", "closedAt": "2026-04-10T10:00:00Z",
}


def artifact_findings(tmp_path, generated, closed=None):
    artifact = tmp_path / "chronology.md"
    header = f"Generated: {generated}\n" if generated is not None else ""
    artifact.write_text(
        header + "Recommended action: close #100.\n",
        encoding="utf-8", newline="\n",
    )
    issue = dict(CLOSED_EXAMPLE)
    if closed is not None:
        issue["closedAt"] = closed
    return roi.audit_issue_hygiene([issue], artifact_paths=[artifact])


def test_post_closure_artifact_is_not_stale(tmp_path):
    assert artifact_findings(tmp_path, "2026-04-10T11:00:00Z") == []


@pytest.mark.parametrize(("generated", "closed", "stale"), [
    ("2026-04-10T09:00:00Z", "2026-04-10T10:00:00Z", True),
    ("2026-04-10T10:00:00Z", "2026-04-10T10:00:00Z", False),
    ("2026-04-10T11:00:00Z", "2026-04-10T10:00:00Z", False),
    ("2026-04-10T11:00:00+02:00", "2026-04-10T10:00:00Z", True),
    ("2026-04-10T09:00:00-02:00", "2026-04-10T10:00:00Z", False),
    ("2026-04-10T11:00:00+02:00", "2026-04-10T09:00:00Z", False),
    ("2026-04-10T09:00:00Z", "2026-04-10T12:00:00+02:00", True),
    ("2026-04-10T09:00:00Z", "2026-04-10T08:00:00-02:00", True),
])
def test_artifact_chronology_uses_instants(tmp_path, generated, closed, stale):
    findings = artifact_findings(tmp_path, generated, closed)
    assert [f["category"] for f in findings] == (["stale-artifact"] if stale else [])
    if stale:
        assert findings[0]["recommendation"] == "refresh"
        assert findings[0]["confidence"] == "high"


@pytest.mark.parametrize("generated", [
    None, "", "not-a-timestamp", "2026-02-30T09:00:00Z",
    "2026-04-10", "2026-04-10T09:00:00",
])
def test_unknown_generation_time_does_not_support_staleness(tmp_path, generated):
    # A recently written file is still unknown when its explicit time is absent.
    assert artifact_findings(tmp_path, generated) == []
    assert roi._artifact_record(tmp_path / "chronology.md")["generated_at"] is None


@pytest.mark.parametrize("closed", [
    None, "", "not-a-timestamp", "2026-02-30T10:00:00Z",
    "2026-04-10", "2026-04-10T10:00:00", 100,
])
def test_unknown_closure_time_does_not_support_staleness(tmp_path, closed):
    artifact = tmp_path / "unknown-closure.md"
    artifact.write_text(
        "generated_at: 2026-04-10T09:00:00Z\nClose #100.\n",
        encoding="utf-8", newline="\n",
    )
    issue = {"number": 100, "state": "CLOSED"}
    if closed is not None:
        issue["closedAt"] = closed
    assert roi.audit_issue_hygiene([issue], artifact_paths=[artifact]) == []


@pytest.mark.parametrize("header", [
    "Generated: 2026-04-10T09:00:00Z",
    'generated_at: "2026-04-10T09:00:00+00:00"',
    "Generated at: 2026-04-10T09:00:00Z",
    "**Generated:** 2026-04-10T09:00:00Z",
])
def test_explicit_generation_metadata_is_timezone_aware(tmp_path, header):
    artifact = tmp_path / "metadata.md"
    artifact.write_text(header + "\nClose #100.\n", encoding="utf-8", newline="\n")
    record = roi._artifact_record(artifact)
    assert record["generated_at"].isoformat() == "2026-04-10T09:00:00+00:00"
    assert roi.audit_issue_hygiene([CLOSED_EXAMPLE], artifact_paths=[artifact])


def test_conflicting_generation_metadata_is_unknown(tmp_path):
    artifact = tmp_path / "conflicting.md"
    artifact.write_text(
        "Generated: 2026-04-10T09:00:00Z\n"
        "generated_at: 2026-04-10T11:00:00Z\nClose #100.\n",
        encoding="utf-8", newline="\n",
    )
    assert roi._artifact_record(artifact)["generated_at"] is None
    assert roi.audit_issue_hygiene([CLOSED_EXAMPLE], artifact_paths=[artifact]) == []


def test_equivalent_generation_metadata_is_known(tmp_path):
    artifact = tmp_path / "equivalent.md"
    artifact.write_text(
        "Generated: 2026-04-10T09:00:00Z\n"
        "generated_at: 2026-04-10T11:00:00+02:00\nClose #100.\n",
        encoding="utf-8", newline="\n",
    )
    assert roi._artifact_record(artifact)["generated_at"] is not None
    findings = roi.audit_issue_hygiene([CLOSED_EXAMPLE], artifact_paths=[artifact])
    assert [f["category"] for f in findings] == ["stale-artifact"]


def test_stale_artifact_only_names_chronologically_supported_issues(tmp_path):
    artifact = tmp_path / "mixed.md"
    artifact.write_text(
        "Generated: 2026-04-10T10:00:00Z\nClose #100, #101, #102, #103.\n",
        encoding="utf-8", newline="\n",
    )
    issues = [
        {"number": 100, "state": "CLOSED", "closedAt": "2026-04-10T11:00:00Z"},
        {"number": 101, "state": "CLOSED", "closedAt": "2026-04-10T09:00:00Z"},
        {"number": 102, "state": "CLOSED"},
        {"number": 103, "state": "OPEN", "closedAt": "2026-04-10T11:00:00Z"},
    ]
    findings = roi.audit_issue_hygiene(issues, artifact_paths=[artifact])
    assert [f["issues"] for f in findings] == [[100]]


def test_closed_parent_history_is_not_drift(tmp_path):
    artifact = tmp_path / "history.md"
    artifact.write_text(
        "History: closed parent #100 established the scope for child #101.\n"
        "Recommended next action: implement #101 independently.\n",
        encoding="utf-8", newline="\n",
    )
    issues = [{"number": 100, "state": "CLOSED"},
              {"number": 101, "state": "OPEN"}]
    assert roi.audit_issue_hygiene(issues, artifact_paths=[artifact]) == []


@pytest.mark.parametrize("routing", [
    "Parent #100 previously routed work through child #101.",
    "Parent #100 no longer routes work through child #101.",
    "Parent #100 does not depend on child #101.",
    "Parent #100 and child #101 share historical context.",
    "Parent #100 mentions #101. Current routing is handled elsewhere.",
    "Parent #100 may route work through child #101.",
    "Parent #100 depends on child #101 only if the proposal is accepted.",
    "Parent #100 depends on child #101?",
    "Parent #100 depends on child #101 in the archived plan.",
    "Parent #100 depends on child #101 unless replaced.",
])
def test_parent_child_mentions_are_not_active_routing(tmp_path, routing):
    artifact = tmp_path / "routing.md"
    artifact.write_text(routing, encoding="utf-8", newline="\n")
    issues = [{"number": 100, "state": "OPEN"},
              {"number": 101, "state": "CLOSED"}]
    assert roi.audit_issue_hygiene(issues, artifact_paths=[artifact]) == []


@pytest.mark.parametrize("routing", [
    "Parent #100 still routes work through child #101.",
    "Umbrella #100 currently routes work through child #101.",
    "Parent #100 depends on child #101.",
    "Child #100 still depends on parent #101.",
])
def test_active_routing_to_closed_issue_is_drift(tmp_path, routing):
    artifact = tmp_path / "active.md"
    artifact.write_text(routing + " Historical context: #102.\n", encoding="utf-8", newline="\n")
    issues = [{"number": 100, "state": "OPEN"},
              {"number": 101, "state": "CLOSED"},
              {"number": 102, "state": "CLOSED"}]
    findings = roi.audit_issue_hygiene(issues, artifact_paths=[artifact])
    assert [f["issues"] for f in findings] == [[100, 101]]
    assert findings[0]["category"] == "parent-child-drift"
    assert findings[0]["recommendation"] == "verify"


@pytest.mark.parametrize(("source", "target"), [
    ("CLOSED", "CLOSED"), ("CLOSED", "OPEN"), ("OPEN", "OPEN"),
])
def test_drift_requires_open_source_and_closed_target(tmp_path, source, target):
    artifact = tmp_path / "inactive.md"
    artifact.write_text(
        "Parent #100 still routes work through child #101.\n",
        encoding="utf-8", newline="\n",
    )
    issues = [{"number": 100, "state": source},
              {"number": 101, "state": target}]
    assert roi.audit_issue_hygiene(issues, artifact_paths=[artifact]) == []


@pytest.mark.parametrize("overlap", [
    "",
    "Same-category siblings #100 and #101 have distinct scope.",
    "#100 and #101 are not duplicates; they address separate components.",
    "No overlap between #100 and #101; these are distinct siblings.",
    "No structural overlap between #100 and #101.",
    "#100 and #101 are not overlapping.",
    "#100 and #101 no longer overlap.",
    "#100 and #101 might overlap.",
    "Duplicate cluster: #100 and #101?",
])
def test_distinct_siblings_are_not_duplicates(overlap):
    issues = [
        {"number": 100, "title": "Audit parser inputs", "state": "OPEN",
         "labels": [{"name": "cat:harness"}], "body": "Sibling of #101."},
        {"number": 101, "title": "Audit parser outputs", "state": "OPEN",
         "labels": [{"name": "cat:harness"}], "body": "Sibling of #100."},
    ]
    assert roi.audit_issue_hygiene(issues, overlap_audit_text=overlap) == []


def test_audit_order_and_recommendations_are_deterministic(tmp_path):
    artifact = tmp_path / "ordered.md"
    artifact.write_text(
        "Generated: 2026-04-10T09:00:00Z\nClose #100.\n"
        "Parent #101 still routes work through child #100.\n",
        encoding="utf-8", newline="\n",
    )
    issues = [CLOSED_EXAMPLE, {"number": 101, "state": "OPEN"}]
    overlap = "Duplicate cluster: #100 and #101 target the same gate."
    forward = roi.audit_issue_hygiene(
        issues, artifact_paths=[artifact], overlap_audit_text=overlap,
    )
    reverse = roi.audit_issue_hygiene(
        list(reversed(issues)), artifact_paths=[artifact, artifact],
        overlap_audit_text=overlap + "\n" + overlap,
    )
    assert forward == reverse
    assert [f["recommendation"] for f in forward] == ["merge", "refresh", "verify"]
    assert roi.format_hygiene_json(forward, "fixed") == roi.format_hygiene_json(
        list(reversed(reverse)), "fixed",
    )


@pytest.mark.parametrize("audit_format", ["json", "markdown"])
def test_audit_cli_uses_only_supplied_fixtures(tmp_path, capsys, audit_format):
    artifact = tmp_path / "fixture.md"
    artifact.write_text(
        "Generated: 2026-04-10T09:00:00Z\nClose #100.\n"
        "Parent #101 still routes work through child #100.\n",
        encoding="utf-8", newline="\n",
    )
    snapshot = tmp_path / "issues.json"
    snapshot.write_text(json.dumps([
        CLOSED_EXAMPLE, {"number": 101, "state": "OPEN"},
    ]), encoding="utf-8", newline="\n")
    overlap = tmp_path / "overlap.md"
    overlap.write_text(
        "Duplicate cluster: #100 and #101 target the same gate.\n",
        encoding="utf-8", newline="\n",
    )
    with patch.object(roi.subprocess, "run", side_effect=AssertionError(
        "Fixture audit must not start any external command",
    )):
        roi.main([
            "--audit", "--issues-json", str(snapshot),
            "--artifact-glob", str(artifact), "--overlap-audit", str(overlap),
            "--repo-root", str(tmp_path), "--audit-format", audit_format,
        ])
    output = capsys.readouterr().out
    if audit_format == "json":
        findings = json.loads(output)["findings"]
        assert [f["recommendation"] for f in findings] == ["merge", "refresh", "verify"]
    else:
        assert "stale-artifact" in output
        assert "parent-child-drift" in output
        assert "duplicate" in output


@pytest.mark.parametrize("overlap", [
    "#100 and #101 are duplicates.",
    "#100 and #101 overlap.",
    "Structural overlap between #100 and #101.",
    "No overlap between #102 and #103; #100 and #101 overlap.",
])
def test_affirmative_overlap_is_scoped_to_its_clause(overlap):
    issues = [{"number": number, "state": "OPEN"} for number in range(100, 104)]
    findings = roi.audit_issue_hygiene(issues, overlap_audit_text=overlap)
    assert [finding["issues"] for finding in findings] == [[100, 101]]
