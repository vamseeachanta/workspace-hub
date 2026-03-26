"""Tests for update-github-issue.py — WRK-1331."""

import os
import sys
import textwrap
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent dir so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import importlib

ugi = importlib.import_module("update-github-issue")


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def repo_root(tmp_path):
    """Create a minimal repo structure with a WRK file."""
    # WRK file in pending/
    pending = tmp_path / ".claude" / "work-queue" / "pending"
    pending.mkdir(parents=True)
    wrk_file = pending / "WRK-9999.md"
    wrk_file.write_text(textwrap.dedent("""\
        ---
        id: WRK-9999
        title: Test feature for issue rendering
        status: pending
        priority: high
        complexity: moderate
        category: engineering
        subcategory: cathodic-protection
        computer: dev-primary
        stage_evidence_ref: .claude/work-queue/assets/WRK-9999/evidence/stage-evidence.yaml
        spec_ref: .planning/archive/modules/WRK-9999/plan.md
        ---
        # Test Feature

        ## Mission
        Build a test feature that does something useful.

        ## Acceptance Criteria
        - [x] First criterion is met
        - [ ] Second criterion pending
        - [x] Third criterion done
    """))
    return tmp_path


@pytest.fixture
def repo_root_full(repo_root):
    """Extend repo_root with all evidence files."""
    assets = repo_root / ".claude" / "work-queue" / "assets" / "WRK-9999" / "evidence"
    assets.mkdir(parents=True)

    # stage-evidence.yaml
    (assets / "stage-evidence.yaml").write_text(textwrap.dedent("""\
        wrk_id: WRK-9999
        stages:
        - order: 1
          stage: Capture
          status: done
          comment: WRK created.
        - order: 2
          stage: Resource Intelligence
          status: done
          comment: Resources gathered.
        - order: 10
          stage: Work Execution
          status: working
          comment: In progress.
    """))

    # execute.yaml
    (assets / "execute.yaml").write_text(textwrap.dedent("""\
        wrk_id: WRK-9999
        stage: 10
        completed_at: "2026-03-19T10:00:00Z"
        commit: "abc123"
        deliverables:
          - path: src/feature.py
            description: "Main feature implementation"
          - path: tests/test_feature.py
            description: "Unit tests"
        test_results:
          passed: 5
          failed: 0
    """))

    # tdd.yaml
    (assets / "tdd.yaml").write_text(textwrap.dedent("""\
        wrk_id: WRK-9999
        approach: red-green-refactor
        tests_total: 5
        tests_passed: 5
        tests_failed: 0
        ac_results:
          - ac: "Feature works end to end"
            result: pass
          - ac: "Edge case handled"
            result: pass
    """))

    # cost-summary.yaml
    (assets / "cost-summary.yaml").write_text(textwrap.dedent("""\
        wrk_id: WRK-9999
        total_input_tokens: 50000
        total_output_tokens: 12000
        estimated_cost_usd: 0.42
    """))

    # future-work.yaml
    (assets / "future-work.yaml").write_text(textwrap.dedent("""\
        wrk_id: WRK-9999
        items:
          - title: "Follow-up optimization"
            priority: medium
            ref: WRK-10001
    """))

    # plan
    plan_dir = repo_root / "specs" / "wrk" / "WRK-9999"
    plan_dir.mkdir(parents=True)
    (plan_dir / "plan.md").write_text(textwrap.dedent("""\
        # Plan for WRK-9999

        ## Approach
        We will implement the feature using TDD.

        ## Steps
        1. Write tests
        2. Implement
        3. Refactor
    """))

    return repo_root


# ── Test Cases ────────────────────────────────────────────────────────


def test_render_body_minimal(repo_root):
    """WRK with only frontmatter, no evidence files."""
    body = ugi.render_body("WRK-9999", repo_root)
    assert "## WRK-9999: Test feature for issue rendering" in body
    assert "**Status:**" in body
    assert "**Priority:** high" in body
    assert "**Category:** engineering/cathodic-protection" in body
    # Missing sections should say "Not yet available"
    assert "Not yet available" in body or "Not yet started" in body


def test_render_body_full(repo_root_full):
    """WRK with all evidence files present."""
    body = ugi.render_body("WRK-9999", repo_root_full)
    assert "## WRK-9999: Test feature for issue rendering" in body
    assert "Main feature implementation" in body
    assert "red-green-refactor" in body
    assert "Capture" in body
    # Should have all collapsible sections
    assert "<details>" in body
    assert "</details>" in body
    assert body.count("<details>") >= 6


def test_extract_acs(repo_root):
    """Extracts checkbox lines from WRK body."""
    acs = ugi.extract_acceptance_criteria("WRK-9999", repo_root)
    assert len(acs) == 3
    assert "- [x] First criterion is met" in acs
    assert "- [ ] Second criterion pending" in acs
    assert "- [x] Third criterion done" in acs


def test_stage_progress_rendering(repo_root_full):
    """Converts stage-evidence.yaml to checkbox list."""
    body = ugi.render_body("WRK-9999", repo_root_full)
    # done stages get checked boxes
    assert "- [x] **1. Capture** — WRK created." in body
    assert "- [x] **2. Resource Intelligence** — Resources gathered." in body
    # working stage gets unchecked
    assert "- [ ] **10. Work Execution** — In progress." in body


def test_implementation_summary(repo_root_full):
    """Renders execute.yaml data."""
    body = ugi.render_body("WRK-9999", repo_root_full)
    assert "src/feature.py" in body
    assert "Main feature implementation" in body
    assert "Passed: 5" in body


def test_tdd_results(repo_root_full):
    """Renders tdd.yaml data."""
    body = ugi.render_body("WRK-9999", repo_root_full)
    assert "red-green-refactor" in body
    assert "5/5 passed" in body
    assert "Feature works end to end" in body


def test_missing_evidence_graceful(repo_root):
    """Missing files produce 'Not yet available'."""
    body = ugi.render_body("WRK-9999", repo_root)
    # Count occurrences of fallback text
    fallback_count = body.count("Not yet available") + body.count("Not yet started")
    # At least implementation, tdd, evidence, stage sections should fall back
    assert fallback_count >= 4


@patch("subprocess.run")
def test_dry_run_no_gh_call(mock_run, repo_root, capsys):
    """dry-run mode doesn't invoke gh."""
    ugi.main(["WRK-9999", "--create", "--dry-run"], repo_root=repo_root)
    mock_run.assert_not_called()
    captured = capsys.readouterr()
    assert "## WRK-9999" in captured.out


@patch("subprocess.run")
def test_create_calls_gh(mock_run, repo_root):
    """--create invokes gh issue create."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="https://github.com/owner/repo/issues/42\n",
    )
    ugi.main(["WRK-9999", "--create"], repo_root=repo_root)
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    cmd = call_args[0][0]
    assert "gh" in cmd
    assert "issue" in cmd
    assert "create" in cmd


@patch("subprocess.run")
def test_create_stores_issue_ref(mock_run, repo_root):
    """--create stores github_issue_ref in WRK frontmatter."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="https://github.com/owner/repo/issues/42\n",
    )
    ugi.main(["WRK-9999", "--create"], repo_root=repo_root)
    wrk_file = repo_root / ".claude" / "work-queue" / "pending" / "WRK-9999.md"
    content = wrk_file.read_text()
    assert "github_issue_ref: https://github.com/owner/repo/issues/42" in content


def test_labels_generated(repo_root):
    """Labels are correctly generated from frontmatter."""
    labels = ugi.generate_labels("WRK-9999", repo_root)
    assert "enhancement" in labels
    assert "priority:high" in labels
    assert "cat:engineering" in labels
