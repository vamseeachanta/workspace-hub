#!/usr/bin/env python3
"""Batch manifest validation CLI for solver queue.

ABOUTME: Validates batch manifest YAML files before submission. Checks schema
structure, required fields, solver type validity, file references, and duplicate
job names. Pydantic-based schema validation with clear error reporting.

Usage:
    uv run python scripts/solver/validate_manifest.py path/to/manifest.yaml
    uv run python scripts/solver/validate_manifest.py manifests/batch.yaml --verbose

Exit codes:
    0 - Manifest is valid
    1 - Manifest has errors
    2 - File not found or parse error
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

try:
    from pydantic import BaseModel, ValidationError, field_validator
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}
SUPPORTED_SCHEMA_VERSIONS = {"1", "1.0"}


# ---------------------------------------------------------------------------
# Validation result
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Result of manifest validation.

    Attributes:
        valid: True if manifest passed all checks.
        errors: List of error messages (blocking).
        warnings: List of warning messages (non-blocking).
    """
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pydantic schema (optional -- falls back to manual validation)
# ---------------------------------------------------------------------------

if HAS_PYDANTIC:
    class JobEntry(BaseModel):
        """Schema for a single job in the batch manifest."""
        name: str
        solver_type: str
        model_file: str
        description: Optional[str] = ""

        @field_validator("solver_type")
        @classmethod
        def validate_solver_type(cls, v: str) -> str:
            if v.lower() not in VALID_SOLVER_TYPES:
                valid_types = sorted(VALID_SOLVER_TYPES)
                raise ValueError(
                    f"Invalid solver_type '{v}'. Must be one of: {valid_types}"
                )
            return v.lower()

    class ManifestSchema(BaseModel):
        """Schema for the batch manifest file."""
        schema_version: Optional[str] = "1"
        jobs: List[JobEntry]
else:
    # Stub classes when pydantic is not available
    class JobEntry:  # type: ignore[no-redef]
        pass

    class ManifestSchema:  # type: ignore[no-redef]
        pass


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------

def _parse_yaml(path: Path) -> tuple[Optional[dict], Optional[str]]:
    """Parse a YAML file, returning (data, error)."""
    if not path.exists():
        return None, f"File not found: {path}"

    try:
        if yaml is not None:
            with open(path) as f:
                data = yaml.safe_load(f)
        else:
            # Minimal fallback
            data = None
            return None, "PyYAML not installed and file is not JSON"

        if not isinstance(data, dict):
            type_name = type(data).__name__
            return None, f"Manifest must be a YAML mapping, got {type_name}"
        return data, None
    except Exception as e:
        return None, f"YAML parse error: {e}"


def check_file_references(manifest_data: dict, base_dir: Path) -> list[str]:
    """Check that model_file paths actually exist.

    Args:
        manifest_data: Parsed manifest dict with 'jobs' key.
        base_dir: Base directory for resolving relative paths.

    Returns:
        List of warning messages for missing files.
    """
    warnings = []
    jobs = manifest_data.get("jobs", [])
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            continue
        model_file = job.get("model_file", "")
        if not model_file:
            continue

        model_path = Path(model_file)
        if not model_path.is_absolute():
            model_path = base_dir / model_file

        if not model_path.exists():
            name = job.get("name", f"job[{i}]")
            warnings.append(
                f"Job '{name}': model_file not found: {model_file}"
            )
    return warnings


def check_duplicates(manifest_data: dict) -> list[str]:
    """Check for duplicate job names in the manifest.

    Args:
        manifest_data: Parsed manifest dict with 'jobs' key.

    Returns:
        List of error messages for duplicate job names.
    """
    errors = []
    jobs = manifest_data.get("jobs", [])
    seen: dict[str, int] = {}

    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            continue
        name = job.get("name", "")
        if not name:
            continue
        if name in seen:
            errors.append(
                f"Duplicate job name '{name}' at indices {seen[name]} and {i}"
            )
        else:
            seen[name] = i

    return errors


def validate_manifest(path: Path) -> ValidationResult:
    """Validate a batch manifest YAML file.

    Checks:
    1. File exists and is valid YAML
    2. Has required 'jobs' key with non-empty list
    3. Each job has required fields (name, solver_type, model_file)
    4. Solver type is valid (orcawave/orcaflex)
    5. No duplicate job names
    6. File references exist (warnings only)
    7. Schema version compatibility

    Args:
        path: Path to the manifest YAML file.

    Returns:
        ValidationResult with valid flag, errors, and warnings.
    """
    result = ValidationResult()

    # Parse YAML
    data, parse_error = _parse_yaml(path)
    if parse_error:
        result.valid = False
        result.errors.append(parse_error)
        return result

    assert data is not None

    # Check schema version
    schema_version = str(data.get("schema_version", "1"))
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        result.warnings.append(
            f"Unsupported schema_version '{schema_version}'. "
            f"Supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}. "
            f"Validation may be incomplete."
        )
        # Unsupported version makes it invalid if it's a future version
        try:
            max_supported = max(float(v) for v in SUPPORTED_SCHEMA_VERSIONS)
            if float(schema_version) > max_supported:
                result.valid = False
                result.errors.append(
                    f"Schema version '{schema_version}' is newer than supported. "
                    f"Please update validate_manifest.py."
                )
                return result
        except ValueError:
            pass

    # Check 'jobs' key
    if "jobs" not in data:
        result.valid = False
        result.errors.append("Manifest must contain a 'jobs' key")
        return result

    jobs = data["jobs"]
    if not isinstance(jobs, list):
        result.valid = False
        result.errors.append("'jobs' must be a list")
        return result

    if len(jobs) == 0:
        result.valid = False
        result.errors.append("'jobs' list is empty -- at least one job required")
        return result

    # Validate each job
    if HAS_PYDANTIC:
        try:
            ManifestSchema(
                schema_version=schema_version,
                jobs=[JobEntry(**job) for job in jobs],
            )
        except (ValidationError, TypeError) as e:
            result.valid = False
            for err_line in str(e).split("\n"):
                if err_line.strip():
                    result.errors.append(err_line.strip())
            return result
    else:
        # Manual validation without pydantic
        for i, job in enumerate(jobs):
            if not isinstance(job, dict):
                result.valid = False
                result.errors.append(f"Job [{i}] is not a mapping")
                continue

            if "solver_type" not in job:
                result.valid = False
                result.errors.append(
                    f"Job [{i}]: missing required field 'solver_type'"
                )

            if "model_file" not in job:
                result.valid = False
                result.errors.append(
                    f"Job [{i}]: missing required field 'model_file'"
                )

            solver = job.get("solver_type", "").lower()
            if solver and solver not in VALID_SOLVER_TYPES:
                solver_val = job.get("solver_type", "")
                result.valid = False
                result.errors.append(
                    f"Job [{i}]: invalid solver_type '{solver_val}'. "
                    f"Must be one of: {sorted(VALID_SOLVER_TYPES)}"
                )

    # Check duplicates
    dupe_errors = check_duplicates(data)
    if dupe_errors:
        result.valid = False
        result.errors.extend(dupe_errors)

    # Check file references (warnings only -- files may exist on target machine)
    if result.valid:
        base_dir = path.parent if path.exists() else Path(".")
        ref_warnings = check_file_references(data, base_dir)
        result.warnings.extend(ref_warnings)

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI entry point for manifest validation."""
    if len(sys.argv) < 2:
        print(
            "Usage: uv run python scripts/solver/validate_manifest.py <manifest.yaml>",
            file=sys.stderr,
        )
        return 2

    manifest_path = Path(sys.argv[1])

    print(f"Validating: {manifest_path}")
    result = validate_manifest(manifest_path)

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for err in result.errors:
            print(f"  x {err}")

    if result.warnings:
        print(f"\nWARNINGS ({len(result.warnings)}):")
        for warn in result.warnings:
            print(f"  ! {warn}")

    if result.valid:
        print("\n[OK] Manifest is valid")
        return 0
    else:
        print("\n[FAIL] Manifest has errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
