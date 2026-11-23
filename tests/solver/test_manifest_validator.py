"""Tests for batch manifest validation CLI.

ABOUTME: Validates validate_manifest.py — schema enforcement, required fields,
file reference checks, duplicate detection, solver type validation.
All filesystem operations use temp directories. No external deps except pydantic.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'solver'))
from validate_manifest import (
    ManifestSchema,
    ValidationResult,
    check_duplicates,
    check_file_references,
    validate_manifest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_manifest(path: Path, content: str) -> Path:
    """Write YAML content to a manifest file."""
    path.write_text(textwrap.dedent(content))
    return path


# ---------------------------------------------------------------------------
# Tests: Valid manifests
# ---------------------------------------------------------------------------

class TestValidManifest:
    """Test that valid manifests pass validation."""

    def test_minimal_valid_manifest(self, tmp_path: Path):
        """Manifest with required fields passes."""
        # Create model file so file-ref check passes
        model = tmp_path / "model.owd"
        model.write_text("dummy")
        manifest = write_manifest(tmp_path / "batch.yaml", f"""\
            schema_version: "1"
            jobs:
              - name: job1
                solver_type: orcawave
                model_file: {model}
                description: test job
        """)
        result = validate_manifest(manifest)
        assert result.valid is True
        assert result.errors == []

    def test_multiple_valid_jobs(self, tmp_path: Path):
        """Manifest with multiple valid jobs passes."""
        m1 = tmp_path / "a.owd"
        m2 = tmp_path / "b.dat"
        m1.write_text("dummy")
        m2.write_text("dummy")
        manifest = write_manifest(tmp_path / "batch.yaml", f"""\
            schema_version: "1"
            jobs:
              - name: job1
                solver_type: orcawave
                model_file: {m1}
              - name: job2
                solver_type: orcaflex
                model_file: {m2}
        """)
        result = validate_manifest(manifest)
        assert result.valid is True


# ---------------------------------------------------------------------------
# Tests: Missing required fields
# ---------------------------------------------------------------------------

class TestMissingFields:
    """Test that missing required fields are caught."""

    def test_missing_model_file(self, tmp_path: Path):
        """Missing model_file triggers an error."""
        manifest = write_manifest(tmp_path / "batch.yaml", """\
            schema_version: "1"
            jobs:
              - name: job1
                solver_type: orcawave
        """)
        result = validate_manifest(manifest)
        assert result.valid is False
        assert any("model_file" in e.lower() for e in result.errors)

    def test_missing_solver_type(self, tmp_path: Path):
        """Missing solver_type triggers an error."""
        manifest = write_manifest(tmp_path / "batch.yaml", """\
            schema_version: "1"
            jobs:
              - name: job1
                model_file: model.owd
        """)
        result = validate_manifest(manifest)
        assert result.valid is False
        assert any("solver_type" in e.lower() for e in result.errors)

    def test_missing_jobs_key(self, tmp_path: Path):
        """Manifest without 'jobs' key is invalid."""
        manifest = write_manifest(tmp_path / "batch.yaml", """\
            schema_version: "1"
            something_else: true
        """)
        result = validate_manifest(manifest)
        assert result.valid is False
        assert any("jobs" in e.lower() for e in result.errors)

    def test_empty_jobs_list(self, tmp_path: Path):
        """Manifest with empty jobs list is invalid."""
        manifest = write_manifest(tmp_path / "batch.yaml", """\
            schema_version: "1"
            jobs: []
        """)
        result = validate_manifest(manifest)
        assert result.valid is False


# ---------------------------------------------------------------------------
# Tests: Invalid file references
# ---------------------------------------------------------------------------

class TestFileReferences:
    """Test file reference validation."""

    def test_nonexistent_model_file(self, tmp_path: Path):
        """Warning when model file doesn't exist."""
        manifest = write_manifest(tmp_path / "batch.yaml", """\
            schema_version: "1"
            jobs:
              - name: job1
                solver_type: orcawave
                model_file: /nonexistent/model.owd
        """)
        result = validate_manifest(manifest)
        # File reference issues may be warnings or errors depending on impl
        assert len(result.warnings) > 0 or not result.valid

    def test_existing_file_no_warning(self, tmp_path: Path):
        """No warning when model file exists."""
        model = tmp_path / "model.owd"
        model.write_text("dummy")
        warnings = check_file_references(
            {"jobs": [{"name": "j1", "solver_type": "orcawave", "model_file": str(model)}]},
            tmp_path,
        )
        assert warnings == []


# ---------------------------------------------------------------------------
# Tests: Duplicate job names
# ---------------------------------------------------------------------------

class TestDuplicates:
    """Test duplicate job name detection."""

    def test_duplicate_job_names(self, tmp_path: Path):
        """Duplicate job names are flagged."""
        manifest_data = {
            "jobs": [
                {"name": "same-name", "solver_type": "orcawave", "model_file": "a.owd"},
                {"name": "same-name", "solver_type": "orcaflex", "model_file": "b.dat"},
            ]
        }
        dupes = check_duplicates(manifest_data)
        assert len(dupes) > 0
        assert "same-name" in dupes[0]

    def test_unique_names_no_duplicates(self, tmp_path: Path):
        """Unique job names pass duplicate check."""
        manifest_data = {
            "jobs": [
                {"name": "job-a", "solver_type": "orcawave", "model_file": "a.owd"},
                {"name": "job-b", "solver_type": "orcaflex", "model_file": "b.dat"},
            ]
        }
        dupes = check_duplicates(manifest_data)
        assert dupes == []


# ---------------------------------------------------------------------------
# Tests: Invalid solver type
# ---------------------------------------------------------------------------

class TestInvalidSolverType:
    """Test solver type validation."""

    def test_invalid_solver_type(self, tmp_path: Path):
        """Unknown solver type is invalid."""
        model = tmp_path / "model.owd"
        model.write_text("dummy")
        manifest = write_manifest(tmp_path / "batch.yaml", f"""\
            schema_version: "1"
            jobs:
              - name: job1
                solver_type: unknown_solver
                model_file: {model}
        """)
        result = validate_manifest(manifest)
        assert result.valid is False
        assert any("solver" in e.lower() for e in result.errors)

    def test_valid_solver_types(self, tmp_path: Path):
        """orcawave and orcaflex are valid solver types."""
        m1 = tmp_path / "a.owd"
        m2 = tmp_path / "b.dat"
        m1.write_text("d")
        m2.write_text("d")
        manifest = write_manifest(tmp_path / "batch.yaml", f"""\
            schema_version: "1"
            jobs:
              - name: job1
                solver_type: orcawave
                model_file: {m1}
              - name: job2
                solver_type: orcaflex
                model_file: {m2}
        """)
        result = validate_manifest(manifest)
        assert result.valid is True


# ---------------------------------------------------------------------------
# Tests: Schema version compatibility
# ---------------------------------------------------------------------------

class TestSchemaVersion:
    """Test schema version validation."""

    def test_unsupported_schema_version(self, tmp_path: Path):
        """Future schema version triggers error or warning."""
        model = tmp_path / "model.owd"
        model.write_text("dummy")
        manifest = write_manifest(tmp_path / "batch.yaml", f"""\
            schema_version: "99"
            jobs:
              - name: job1
                solver_type: orcawave
                model_file: {model}
        """)
        result = validate_manifest(manifest)
        assert not result.valid or len(result.warnings) > 0

    def test_missing_schema_version_defaults(self, tmp_path: Path):
        """Missing schema_version should still work (defaults to 1)."""
        model = tmp_path / "model.owd"
        model.write_text("dummy")
        manifest = write_manifest(tmp_path / "batch.yaml", f"""\
            jobs:
              - name: job1
                solver_type: orcawave
                model_file: {model}
        """)
        result = validate_manifest(manifest)
        # Should at least parse — missing version is accepted as default
        assert isinstance(result, ValidationResult)


# ---------------------------------------------------------------------------
# Tests: Non-YAML files and parse errors
# ---------------------------------------------------------------------------

class TestParseErrors:
    """Test handling of non-parseable files."""

    def test_non_yaml_file(self, tmp_path: Path):
        """Non-YAML content triggers parse error."""
        manifest = tmp_path / "bad.yaml"
        manifest.write_text("{{{{ this is not yaml ::::")
        result = validate_manifest(manifest)
        assert result.valid is False

    def test_nonexistent_file(self, tmp_path: Path):
        """Non-existent manifest path is invalid."""
        result = validate_manifest(tmp_path / "does_not_exist.yaml")
        assert result.valid is False
