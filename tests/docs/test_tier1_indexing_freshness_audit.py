"""Tests for the tier-1 indexing freshness audit contract doc and report shape.

Issue: #2465 — daily tier-1 indexing freshness audit.
Plan:  docs/plans/2026-04-22-issue-2465-daily-tier1-indexing-freshness-audit.md
Contract: docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md
Upstream contract: docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md"
UPSTREAM_CONTRACT = (
    REPO_ROOT / "docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md"
)
LATEST_REPORT = REPO_ROOT / "docs/reports/tier-1-indexing-freshness-latest.md"
BUSINESS_BRAIN = REPO_ROOT / "docs/BUSINESS_BRAIN.md"
SCHEDULE_YAML = REPO_ROOT / "config/scheduled-tasks/schedule-tasks.yaml"
CADENCES_YAML = REPO_ROOT / "data/document-index/freshness-cadences.yaml"
PLANS_README = REPO_ROOT / "docs/plans/README.md"

NEGATIVE_AUTHORITY_SENTENCE = (
    "MUST NOT treat any tier-1 indexing scorecard under docs/reports/ "
    "as required canonical authority"
)
TIER1_REPOS = ("workspace-hub", "digitalmodel", "assetutilities", "aceengineer-website")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    assert match, f"missing section: {heading}"
    return match.group("body")


# ─── Contract doc ──────────────────────────────────────────────────────────


def test_contract_doc_exists() -> None:
    assert CONTRACT.exists(), f"missing audit contract doc at {CONTRACT}"


def test_contract_has_required_sections() -> None:
    text = _read(CONTRACT)
    required_headings = [
        "## Scope",
        "## Inputs",
        "## Per-Repo Checks",
        "## Per-Repo Scan-Root Table",
        "## Pass/Fail Thresholds",
        "## Escalation",
        "## Negative-Authority Clause",
        "## Legacy-Pattern Avoidance",
        "## Routine-Management Appendix",
    ]
    for heading in required_headings:
        assert heading in text, f"missing required section heading: {heading}"


def test_contract_has_per_repo_scan_root_table_for_every_tier1_repo() -> None:
    section = _section(_read(CONTRACT), "Per-Repo Scan-Root Table")
    for repo in TIER1_REPOS:
        assert repo in section, (
            f"per-repo scan-root table missing row for tier-1 repo: {repo}"
        )


def test_contract_has_negative_authority_sentence_verbatim() -> None:
    text = _read(CONTRACT)
    assert NEGATIVE_AUTHORITY_SENTENCE in text


def test_contract_three_level_exit_codes_documented() -> None:
    section = _section(_read(CONTRACT), "Escalation")
    for token in ("exit 0", "exit 1", "exit 2", "green", "yellow", "red"):
        assert token in section, f"escalation section missing token: {token}"


def test_contract_routine_management_cites_daily_readiness_pattern() -> None:
    section = _section(_read(CONTRACT), "Routine-Management Appendix")
    assert "aefef5167f2f" in section, (
        "routine-management appendix must name the existing remote routine"
    )
    assert "project_daily_readiness_cron.md" in section or "daily-readiness" in section


def test_contract_states_dated_snapshot_policy() -> None:
    text = _read(CONTRACT)
    assert "dated snapshot" in text.lower(), (
        "contract must declare dated-snapshot retention policy"
    )


def test_contract_cites_upstream_contract_dependency() -> None:
    text = _read(CONTRACT)
    assert "TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md" in text


def test_contract_lists_required_surfaces_from_upstream() -> None:
    text = _read(CONTRACT)
    for surface in (
        "AGENTS.md",
        "README.md",
        "docs/README.md",
        "docs/maps/<repo>-operator-map.md",
        "docs/registry/module-routing.yaml",
    ):
        assert surface in text, f"contract must list required surface: {surface}"


# ─── Latest report ─────────────────────────────────────────────────────────


def test_latest_report_exists() -> None:
    assert LATEST_REPORT.exists(), f"missing latest freshness report at {LATEST_REPORT}"


def test_latest_report_in_body_timestamp_within_48h_window() -> None:
    text = _read(LATEST_REPORT)
    match = re.search(
        r"^Generated:\s*(?P<ts>\S+)",
        text,
        flags=re.MULTILINE,
    )
    assert match, "report must contain in-body 'Generated: <iso8601>' timestamp"
    raw = match.group("ts")
    try:
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        pytest.fail(f"Generated timestamp not iso8601: {raw!r} ({exc})")
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - ts
    assert age <= timedelta(hours=48), (
        f"latest freshness report is older than 48h (age={age})"
    )


def test_latest_report_covers_all_tier1_repos_from_business_brain() -> None:
    """Parse tier-1 repo set from BUSINESS_BRAIN.md and require each appears in report.

    Parsing rule per plan: extract leading pipe-delimited cells between
    ``### Tier-1`` heading and the next ``### Tier-`` heading.
    """
    brain = _read(BUSINESS_BRAIN)
    block = re.search(
        r"^### Tier-1\b.*?(?=^### Tier-)",
        brain,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert block, "BUSINESS_BRAIN.md must have a parseable ### Tier-1 section"
    repos = []
    for line in block.group(0).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|-") or "Repo" in stripped:
            continue
        # leading pipe-delimited cell
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and cells[0]:
            repos.append(cells[0])
    assert repos, "could not parse any tier-1 repos from BUSINESS_BRAIN.md"
    report = _read(LATEST_REPORT)
    for repo in repos:
        assert repo in report, f"freshness report missing tier-1 repo: {repo}"


def test_latest_report_has_negative_authority_disclaimer() -> None:
    text = _read(LATEST_REPORT)
    assert NEGATIVE_AUTHORITY_SENTENCE in text, (
        "report body must include the negative-authority disclaimer verbatim"
    )


def test_latest_report_required_sections_present() -> None:
    text = _read(LATEST_REPORT)
    for heading in (
        "## Overall Status",
        "## Repo Status",
        "## Assumption Check",
    ):
        assert heading in text, f"report missing section: {heading}"
    # per-repo subsections
    for repo in TIER1_REPOS:
        assert re.search(
            rf"^### {re.escape(repo)} — (green|yellow|red)\b",
            text,
            flags=re.MULTILINE,
        ), f"report missing per-repo subsection with status for {repo}"
    # subsection labels
    assert "Current concerns" in text
    assert "Next actions" in text


def test_latest_report_cites_only_existing_files() -> None:
    """Every cited path inside backticks/code-spans must resolve under REPO_ROOT.

    Heuristic: a citation token starts with one of (docs/, scripts/, config/,
    data/, tests/, knowledge/, .claude/, .planning/) and ends in a file
    extension or is a clear directory path. We skip obvious non-paths
    (URLs, GitHub issue refs).
    """
    text = _read(LATEST_REPORT)
    candidates = re.findall(r"`([^`]+)`", text)
    bad = []
    for token in candidates:
        token = token.strip()
        if not token:
            continue
        if any(
            token.startswith(prefix)
            for prefix in (
                "docs/",
                "scripts/",
                "config/",
                "data/",
                "tests/",
                "knowledge/",
                ".claude/",
                ".planning/",
                "logs/",
            )
        ):
            # strip optional trailing punctuation
            token_path = token.rstrip(",.;)")
            # tolerate placeholders like docs/maps/<repo>-operator-map.md
            if "<" in token_path or ">" in token_path:
                continue
            target = REPO_ROOT / token_path
            if not target.exists():
                bad.append(token_path)
    assert not bad, f"freshness report cites non-existent files: {bad[:5]}"


def test_latest_report_red_has_action_required_prefix_when_red() -> None:
    text = _read(LATEST_REPORT)
    overall = _section(text, "Overall Status")
    if "red" in overall.split("\n", 3)[1] if len(overall.split("\n")) > 1 else False:
        # rough check: portfolio red anywhere in overall section
        pass
    # Robust check: scan first 200 chars for status word
    head = text[:1500]
    portfolio_match = re.search(r"Portfolio status:\s*(green|yellow|red)", head)
    if portfolio_match and portfolio_match.group(1) == "red":
        assert "Action required:" in text, (
            "red portfolio reports must include an 'Action required:' header prefix"
        )


# ─── Cadence registry ──────────────────────────────────────────────────────


def test_freshness_cadence_registered_or_cited() -> None:
    """Either a daily cadence entry registers tier-1-indexing-freshness, OR
    the contract doc cites an existing daily entry that applies."""
    cadences = yaml.safe_load(CADENCES_YAML.read_text(encoding="utf-8"))
    have_entry = any(
        c.get("asset_type") == "tier-1-indexing-freshness"
        and c.get("expected_cadence") == "daily"
        for c in cadences.get("cadences", [])
    )
    contract_text = _read(CONTRACT)
    cites_existing = "freshness-cadences.yaml" in contract_text and re.search(
        r"existing daily cadence", contract_text, flags=re.IGNORECASE
    )
    assert have_entry or cites_existing, (
        "register a daily cadence entry OR cite an existing applicable entry "
        "in the contract doc"
    )


# ─── Schedule-tasks YAML ──────────────────────────────────────────────────


def test_schedule_task_entry_exists_with_required_fields() -> None:
    data = yaml.safe_load(SCHEDULE_YAML.read_text(encoding="utf-8"))
    tasks = {t["id"]: t for t in data.get("tasks", [])}
    assert "tier1-indexing-freshness" in tasks, (
        "config/scheduled-tasks/schedule-tasks.yaml must declare "
        "tier1-indexing-freshness task"
    )
    task = tasks["tier1-indexing-freshness"]
    assert task["schedule"] == "30 6 * * *"
    machines = task.get("machines", [])
    assert "dev-primary" in machines
    assert "ace-linux-1" in machines
    requires = task.get("requires", [])
    assert "bash" in requires
    assert "git" in requires
    assert task.get("is_claude_task") is False
    cmd = task.get("command", "")
    assert "scripts/cron/tier1-indexing-freshness.sh" in cmd


def test_schedule_yaml_passes_existing_validator() -> None:
    """Run scripts/cron/validate-schedule.py against the updated YAML."""
    import subprocess

    res = subprocess.run(
        ["uv", "run", "python", str(REPO_ROOT / "scripts/cron/validate-schedule.py")],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "PATH": os.environ.get("PATH", "")},
    )
    assert res.returncode == 0, (
        f"schedule validator failed: stdout={res.stdout!r} stderr={res.stderr!r}"
    )


# ─── Plans README index ───────────────────────────────────────────────────


def test_plans_readme_indexes_2465() -> None:
    text = _read(PLANS_README)
    assert "2465" in text, "docs/plans/README.md must reference issue #2465"
