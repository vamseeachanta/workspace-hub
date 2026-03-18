"""Tests for verify_checklist.py --dry-run flag and core functionality."""

import os
import subprocess
import sys
import tempfile

import pytest
import yaml

# Add parent dir to path so we can import verify_checklist
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from verify_checklist import verify_checklist


@pytest.fixture
def stage_yaml_with_checklist(tmp_path):
    """Create a stage YAML file with checklist items."""
    stage_file = tmp_path / "stage-10-execute.yaml"
    stage_file.write_text(yaml.dump({
        "order": 10,
        "name": "Work Execution",
        "checklist": [
            {"id": "CL-10-1", "text": "Scripts-over-LLM audit performed"},
            {"id": "CL-10-2", "text": "Tests written BEFORE implementation"},
            {"id": "CL-10-3", "text": "All tests pass", "requires_human": True},
        ],
    }))
    return str(stage_file)


@pytest.fixture
def stage_yaml_empty_checklist(tmp_path):
    """Create a stage YAML file with no checklist items."""
    stage_file = tmp_path / "stage-99-empty.yaml"
    stage_file.write_text(yaml.dump({
        "order": 99,
        "name": "Empty Stage",
        "checklist": [],
    }))
    return str(stage_file)


@pytest.fixture
def evidence_dir(tmp_path):
    """Create an evidence directory."""
    ev_dir = tmp_path / "evidence"
    ev_dir.mkdir()
    return str(ev_dir)


class TestDryRunProgrammaticAPI:
    """Test dry_run=True via the Python API."""

    def test_dry_run_returns_items_without_validation(
        self, stage_yaml_with_checklist, evidence_dir
    ):
        result = verify_checklist(
            stage_yaml_with_checklist, "WRK-9999", 10, evidence_dir, dry_run=True
        )
        assert result["passed"] is True
        assert result["blockers"] == []
        assert len(result["items"]) == 3

    def test_dry_run_returns_correct_item_ids(
        self, stage_yaml_with_checklist, evidence_dir
    ):
        result = verify_checklist(
            stage_yaml_with_checklist, "WRK-9999", 10, evidence_dir, dry_run=True
        )
        ids = [item["id"] for item in result["items"]]
        assert ids == ["CL-10-1", "CL-10-2", "CL-10-3"]

    def test_dry_run_empty_checklist(
        self, stage_yaml_empty_checklist, evidence_dir
    ):
        result = verify_checklist(
            stage_yaml_empty_checklist, "WRK-9999", 99, evidence_dir, dry_run=True
        )
        assert result["passed"] is True
        assert result["blockers"] == []
        assert result["items"] == []

    def test_dry_run_ignores_missing_evidence(
        self, stage_yaml_with_checklist
    ):
        """dry_run should work even if evidence_dir doesn't exist."""
        result = verify_checklist(
            stage_yaml_with_checklist, "WRK-9999", 10,
            "/nonexistent/path", dry_run=True
        )
        assert result["passed"] is True
        assert len(result["items"]) == 3


class TestNormalMode:
    """Test normal (non-dry-run) mode still works correctly."""

    def test_normal_mode_blocks_on_missing_evidence(
        self, stage_yaml_with_checklist, evidence_dir
    ):
        result = verify_checklist(
            stage_yaml_with_checklist, "WRK-9999", 10, evidence_dir, dry_run=False
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 3

    def test_normal_mode_passes_with_complete_evidence(
        self, stage_yaml_with_checklist, evidence_dir
    ):
        # Write complete evidence
        ev_file = os.path.join(evidence_dir, "checklist-10.yaml")
        with open(ev_file, "w") as f:
            yaml.dump({
                "items": [
                    {"id": "CL-10-1", "completed": True},
                    {"id": "CL-10-2", "completed": True},
                    {"id": "CL-10-3", "completed": True, "approved_by": "user"},
                ]
            }, f)
        result = verify_checklist(
            stage_yaml_with_checklist, "WRK-9999", 10, evidence_dir, dry_run=False
        )
        assert result["passed"] is True
        assert result["blockers"] == []

    def test_normal_mode_blocks_human_item_without_approved_by(
        self, stage_yaml_with_checklist, evidence_dir
    ):
        ev_file = os.path.join(evidence_dir, "checklist-10.yaml")
        with open(ev_file, "w") as f:
            yaml.dump({
                "items": [
                    {"id": "CL-10-1", "completed": True},
                    {"id": "CL-10-2", "completed": True},
                    {"id": "CL-10-3", "completed": True},  # missing approved_by
                ]
            }, f)
        result = verify_checklist(
            stage_yaml_with_checklist, "WRK-9999", 10, evidence_dir, dry_run=False
        )
        assert result["passed"] is False
        assert len(result["blockers"]) == 1
        assert result["blockers"][0]["id"] == "CL-10-3"

    def test_empty_checklist_passes(
        self, stage_yaml_empty_checklist, evidence_dir
    ):
        result = verify_checklist(
            stage_yaml_empty_checklist, "WRK-9999", 99, evidence_dir, dry_run=False
        )
        assert result["passed"] is True


class TestCLIDryRun:
    """Test --dry-run via CLI subprocess."""

    def test_cli_dry_run_exit_code_zero(self):
        """--dry-run should exit 0 for any valid stage."""
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))
        script = os.path.join(repo_root, "scripts", "work-queue", "verify_checklist.py")
        result = subprocess.run(
            ["uv", "run", "--no-project", "python", script,
             "--dry-run", "WRK-9999", "10"],
            capture_output=True, text=True, cwd=repo_root,
        )
        assert result.returncode == 0
        assert "DRY-RUN:" in result.stdout

    def test_cli_dry_run_shows_item_count(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))
        script = os.path.join(repo_root, "scripts", "work-queue", "verify_checklist.py")
        result = subprocess.run(
            ["uv", "run", "--no-project", "python", script,
             "--dry-run", "WRK-9999", "10"],
            capture_output=True, text=True, cwd=repo_root,
        )
        assert "checklist items:" in result.stdout
