"""Tests for batch job submission via YAML manifest.

ABOUTME: Validates scripts/solver/submit-batch.sh behavior by testing the
companion Python helper that parses YAML manifests and invokes submit-job.sh
per entry.  All git/filesystem operations are mocked.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'solver'))
from validate_manifest import validate_manifest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_MANIFEST = textwrap.dedent("""\
    schema_version: "1"
    jobs:
      - name: l00-smoke-test
        solver_type: orcawave
        model_file: docs/domains/orcawave/L00_validation_wamit/2.1/test01.owd
        description: "L00 smoke test"
      - name: mooring-run
        solver_type: orcaflex
        model_file: models/mooring_analysis.dat
        description: "Mooring run"
      - name: l01-frequency-sweep
        solver_type: orcawave
        model_file: docs/domains/orcawave/L01/test02.owd
        description: "L01 frequency sweep"
""")

MINIMAL_MANIFEST = textwrap.dedent("""\
    schema_version: "1"
    jobs:
      - name: minimal-job
        solver_type: orcawave
        model_file: test.owd
""")

EMPTY_MANIFEST = textwrap.dedent("""\
    schema_version: "1"
    jobs: []
""")

MISSING_SOLVER_MANIFEST = textwrap.dedent("""\
    schema_version: "1"
    jobs:
      - name: missing-solver
        model_file: test.owd
        description: "Missing solver field"
""")

MISSING_INPUT_MANIFEST = textwrap.dedent("""\
    schema_version: "1"
    jobs:
      - name: missing-model-file
        solver_type: orcawave
        description: "Missing model_file field"
""")

NO_JOBS_KEY_MANIFEST = textwrap.dedent("""\
    other_key: value
""")


@pytest.fixture
def manifest_dir(tmp_path: Path) -> Path:
    """Create a temp directory with a valid manifest file."""
    manifest = tmp_path / "batch-manifest.yaml"
    manifest.write_text(VALID_MANIFEST)
    return tmp_path


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    """Create a mock repo root with submit-job.sh."""
    solver_dir = tmp_path / "scripts" / "solver"
    solver_dir.mkdir(parents=True)
    submit_script = solver_dir / "submit-job.sh"
    submit_script.write_text("#!/bin/bash\necho submitted\n")
    submit_script.chmod(0o755)
    return tmp_path


# ---------------------------------------------------------------------------
# Helper: parse_batch_manifest (mirrors the logic in submit-batch.sh)
# ---------------------------------------------------------------------------

def parse_batch_manifest(manifest_path: str | Path) -> list[dict]:
    """Parse a batch manifest YAML file and return list of job dicts.

    Each job dict must have at least 'name', 'solver_type', and 'model_file' keys.
    Raises ValueError for missing required fields or malformed YAML.
    """
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "jobs" not in data:
        raise ValueError("Manifest must contain a 'jobs' key")

    jobs = data["jobs"]
    if not isinstance(jobs, list):
        raise ValueError("'jobs' must be a list")

    validated = []
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise ValueError(f"Job {i} must be a mapping, got {type(job).__name__}")
        if "name" not in job:
            raise ValueError(f"Job {i} missing required field: name")
        if "solver_type" not in job:
            raise ValueError(f"Job {i} missing required field: solver_type")
        if "model_file" not in job:
            raise ValueError(f"Job {i} missing required field: model_file")
        if job["solver_type"] not in ("orcawave", "orcaflex"):
            raise ValueError(
                f"Job {i} invalid solver '{job['solver_type']}' — must be 'orcawave' or 'orcaflex'"
            )
        validated.append(job)
    return validated


def submit_batch(
    manifest_path: str | Path,
    repo_root: str | Path,
    dry_run: bool = False,
    skip_validation: bool = False,
) -> list[dict]:
    """Submit all jobs from a batch manifest.

    Returns list of results: {job: dict, status: str, message: str}
    """
    if not skip_validation:
        validation = validate_manifest(Path(manifest_path))
        if not validation.valid:
            raise ValueError("Manifest validation failed")

    jobs = parse_batch_manifest(manifest_path)
    results = []
    repo = Path(repo_root)
    submit_script = repo / "scripts" / "solver" / "submit-job.sh"

    if not submit_script.exists():
        raise FileNotFoundError(f"submit-job.sh not found at: {submit_script}")

    for job in jobs:
        solver = job["solver_type"]
        input_file = job["model_file"]
        description = job.get("description") or job["name"]

        if dry_run:
            results.append({
                "job": job,
                "status": "dry-run",
                "message": f"Would submit: {solver} {input_file}",
            })
            continue

        try:
            cmd = ["bash", str(submit_script), solver, input_file, description]
            result = subprocess.run(
                cmd,
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                results.append({
                    "job": job,
                    "status": "submitted",
                    "message": result.stdout.strip(),
                })
            else:
                results.append({
                    "job": job,
                    "status": "error",
                    "message": result.stderr.strip(),
                })
        except subprocess.TimeoutExpired:
            results.append({
                "job": job,
                "status": "error",
                "message": "Submission timed out after 60s",
            })

    return results


# ---------------------------------------------------------------------------
# Tests: YAML manifest parsing
# ---------------------------------------------------------------------------

class TestManifestParsing:
    """Test YAML manifest parsing and validation."""

    def test_parse_valid_manifest(self, tmp_path: Path):
        """Valid manifest with 3 jobs parses correctly."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(VALID_MANIFEST)
        jobs = parse_batch_manifest(manifest)
        assert len(jobs) == 3
        assert jobs[0]["solver_type"] == "orcawave"
        assert jobs[1]["solver_type"] == "orcaflex"
        assert jobs[2]["description"] == "L01 frequency sweep"

    def test_parse_minimal_manifest(self, tmp_path: Path):
        """Minimal manifest with one job and no description."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(MINIMAL_MANIFEST)
        jobs = parse_batch_manifest(manifest)
        assert len(jobs) == 1
        assert jobs[0]["solver_type"] == "orcawave"
        assert "description" not in jobs[0]

    def test_parse_empty_jobs_list(self, tmp_path: Path):
        """Empty jobs list returns empty list."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(EMPTY_MANIFEST)
        jobs = parse_batch_manifest(manifest)
        assert jobs == []

    def test_missing_manifest_file(self):
        """Non-existent manifest raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            parse_batch_manifest("/nonexistent/manifest.yaml")

    def test_missing_jobs_key(self, tmp_path: Path):
        """Manifest without 'jobs' key raises ValueError."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(NO_JOBS_KEY_MANIFEST)
        with pytest.raises(ValueError, match="must contain a 'jobs' key"):
            parse_batch_manifest(manifest)


class TestManifestValidation:
    """Test field-level validation of job entries."""

    def test_missing_solver_field(self, tmp_path: Path):
        """Job without 'solver' raises ValueError."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(MISSING_SOLVER_MANIFEST)
        with pytest.raises(ValueError, match="missing required field: solver_type"):
            parse_batch_manifest(manifest)

    def test_missing_input_file_field(self, tmp_path: Path):
        """Job without 'input_file' raises ValueError."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(MISSING_INPUT_MANIFEST)
        with pytest.raises(ValueError, match="missing required field: model_file"):
            parse_batch_manifest(manifest)

    def test_invalid_solver_type(self, tmp_path: Path):
        """Job with unknown solver raises ValueError."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(textwrap.dedent("""\
            schema_version: "1"
            jobs:
              - name: invalid-solver
                solver_type: abaqus
                model_file: model.inp
        """))
        with pytest.raises(ValueError, match="invalid solver 'abaqus'"):
            parse_batch_manifest(manifest)

    def test_malformed_job_entry(self, tmp_path: Path):
        """Non-dict job entry raises ValueError."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(textwrap.dedent("""\
            jobs:
              - "just a string"
        """))
        with pytest.raises(ValueError, match="must be a mapping"):
            parse_batch_manifest(manifest)

    def test_job_count_extraction(self, tmp_path: Path):
        """Verify exact job count from multi-job manifest."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(VALID_MANIFEST)
        jobs = parse_batch_manifest(manifest)
        assert len(jobs) == 3


class TestDryRunMode:
    """Test --dry-run flag behavior."""

    def test_dry_run_does_not_call_subprocess(self, tmp_path: Path, repo_root: Path):
        """Dry-run mode skips actual subprocess calls."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(VALID_MANIFEST)

        with patch("subprocess.run") as mock_run:
            results = submit_batch(manifest, repo_root, dry_run=True)
            mock_run.assert_not_called()

        assert len(results) == 3
        assert all(r["status"] == "dry-run" for r in results)

    def test_dry_run_reports_all_jobs(self, tmp_path: Path, repo_root: Path):
        """Dry-run produces one result per job with descriptive message."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(VALID_MANIFEST)
        results = submit_batch(manifest, repo_root, dry_run=True)

        assert len(results) == 3
        assert "Would submit: orcawave" in results[0]["message"]
        assert "Would submit: orcaflex" in results[1]["message"]

    def test_dry_run_preserves_job_data(self, tmp_path: Path, repo_root: Path):
        """Dry-run results carry original job dicts."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(MINIMAL_MANIFEST)
        results = submit_batch(manifest, repo_root, dry_run=True)

        assert results[0]["job"]["solver_type"] == "orcawave"
        assert results[0]["job"]["model_file"] == "test.owd"


class TestValidationPreflight:
    """Test validate_manifest pre-flight behavior."""

    def test_rejects_empty_jobs_manifest(self, tmp_path: Path, repo_root: Path):
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(EMPTY_MANIFEST)

        with pytest.raises(ValueError, match="Manifest validation failed"):
            submit_batch(manifest, repo_root, dry_run=True)

    def test_rejects_duplicate_job_names(self, tmp_path: Path, repo_root: Path):
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(textwrap.dedent("""\
            schema_version: "1"
            jobs:
              - name: same-job
                solver_type: orcawave
                model_file: first.owd
              - name: same-job
                solver_type: orcaflex
                model_file: second.dat
        """))

        with pytest.raises(ValueError, match="Manifest validation failed"):
            submit_batch(manifest, repo_root, dry_run=True)

    def test_skip_validation_allows_duplicate_job_names(self, tmp_path: Path, repo_root: Path):
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(textwrap.dedent("""\
            schema_version: "1"
            jobs:
              - name: same-job
                solver_type: orcawave
                model_file: first.owd
              - name: same-job
                solver_type: orcaflex
                model_file: second.dat
        """))

        results = submit_batch(manifest, repo_root, dry_run=True, skip_validation=True)
        assert len(results) == 2
        assert all(result["status"] == "dry-run" for result in results)


class TestBatchSubmission:
    """Test actual batch submission with mocked subprocess."""

    def test_successful_submission(self, tmp_path: Path, repo_root: Path):
        """Successful submit-job.sh calls produce 'submitted' status."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(VALID_MANIFEST)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Job submitted: queue/pending/test.yaml"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            results = submit_batch(manifest, repo_root, dry_run=False)

        assert mock_run.call_count == 3
        assert all(r["status"] == "submitted" for r in results)

    def test_failed_submission_captured(self, tmp_path: Path, repo_root: Path):
        """Failed submit-job.sh calls produce 'error' status."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(MINIMAL_MANIFEST)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "ERROR: input file not found"

        with patch("subprocess.run", return_value=mock_result):
            results = submit_batch(manifest, repo_root, dry_run=False)

        assert results[0]["status"] == "error"
        assert "input file not found" in results[0]["message"]

    def test_missing_submit_script(self, tmp_path: Path):
        """Missing submit-job.sh raises FileNotFoundError."""
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(MINIMAL_MANIFEST)
        empty_root = tmp_path / "empty_repo"
        empty_root.mkdir()

        with pytest.raises(FileNotFoundError, match="submit-job.sh not found"):
            submit_batch(manifest, empty_root, dry_run=False)
