"""Validation tests for the #2508 semiconductor CAD/FEM knowledge base."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "docs/reports/semiconductor-cad-fem-knowledge-base.md"
MATRIX_PATH = REPO_ROOT / "data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml"


REQUIRED_ROLE_FAMILIES = {
    "ic-packaging-simulation",
    "semiconductor-mechanical-thermal-engineer",
    "advanced-packaging-engineer",
    "asic-eda-technical-program-role",
    "physical-design-eda-flow-learner-track",
    "layout-cad-automation-track",
}

REQUIRED_DOMAINS = {
    "eda-flow",
    "layout-cad-automation",
    "package-fem-thermal-mechanical",
}

REQUIRED_CHILD_ISSUES = {"#2507", "#2509", "#2510", "#2511", "#2512"}

FORBIDDEN_STANDARDS_CLAIMS = (
    "JEDEC-compliant",
    "IPC-compliant",
    "extracted from JEDEC",
    "extracted from IPC",
)


def _report_text() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


def _matrix() -> dict:
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def test_report_and_yaml_exist() -> None:
    assert REPORT_PATH.exists(), f"missing report: {REPORT_PATH}"
    assert MATRIX_PATH.exists(), f"missing matrix: {MATRIX_PATH}"


def test_yaml_has_required_role_families_and_domains() -> None:
    matrix = _matrix()
    role_families = matrix.get("role_families", [])
    role_ids = {row["id"] for row in role_families}
    domains = {domain for row in role_families for domain in row.get("domains", [])}

    assert len(role_families) >= 6
    assert REQUIRED_ROLE_FAMILIES <= role_ids
    assert REQUIRED_DOMAINS <= domains

    for row in role_families:
        for key in (
            "target_titles",
            "required_skills",
            "tools",
            "local_evidence",
            "source_limitations",
            "portfolio_artifacts",
            "child_issues_or_followups",
        ):
            assert row.get(key), f"{row['id']} missing {key}"


def test_job_evidence_is_curated_and_cited() -> None:
    matrix = _matrix()
    job_evidence = matrix.get("job_evidence", [])
    source_files = {row.get("source_file") for row in job_evidence}
    titles = {row["title"] for row in job_evidence}

    assert len(job_evidence) >= 6
    assert len(source_files) >= 3
    assert "Staff Engineer, Semi Packaging Engineering" in titles
    assert all(str(path).startswith("docs/strategy/gtm/job-market-scan/raw-results/") for path in source_files)
    assert all("adjacent" not in row.get("relevance", "").lower() for row in job_evidence)

    report = _report_text()
    for row in job_evidence:
        assert row["title"] in report
        assert row["source_file"] in report


def test_tool_practice_map_has_supported_sources() -> None:
    matrix = _matrix()
    tool_practices = matrix.get("tool_practices", [])

    assert len(tool_practices) >= 8
    for row in tool_practices:
        assert row.get("tool")
        assert row.get("practice")
        assert row.get("source_url") or row.get("source_path")
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(row.get("accessed"))), row
        assert row.get("supports"), row


def test_report_contains_per_role_mapping_details() -> None:
    report = _report_text()
    required_phrases = (
        "## Detailed Role Mapping",
        "Tools",
        "Local evidence",
        "Source limits",
        "Child / follow-up",
    )
    for phrase in required_phrases:
        assert phrase in report

    for role_id in REQUIRED_ROLE_FAMILIES:
        assert role_id in report


def test_report_links_child_issues_and_downstream_updates() -> None:
    report = _report_text()

    for issue in REQUIRED_CHILD_ISSUES:
        assert issue in report
    assert "Proposed Downstream Issue Updates" in report
    assert "No downstream GitHub issue bodies or comments were edited by #2508" in report


def test_no_overclaiming_standards_access() -> None:
    report = _report_text()
    matrix = _matrix()

    assert "JEDEC/IPC access limitations" in report
    assert "restricted or not locally ingested" in report
    for forbidden in FORBIDDEN_STANDARDS_CLAIMS:
        assert forbidden not in report
        assert forbidden not in MATRIX_PATH.read_text(encoding="utf-8")

    standards = matrix.get("standards_and_source_limits", [])
    assert any("JEDEC" in row.get("name", "") and row.get("access_status") for row in standards)
    assert any("IPC" in row.get("name", "") and row.get("access_status") for row in standards)


def test_report_covers_each_domain_with_portfolio_artifact() -> None:
    matrix = _matrix()
    domains_with_artifacts = {
        domain
        for row in matrix.get("role_families", [])
        if row.get("portfolio_artifacts")
        for domain in row.get("domains", [])
    }

    assert REQUIRED_DOMAINS <= domains_with_artifacts

    report = _report_text()
    for heading in (
        "EDA flow",
        "Layout/CAD automation",
        "Package FEM / thermal-mechanical analysis",
    ):
        assert heading in report
