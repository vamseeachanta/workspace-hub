"""
T1-T4: Stage 1 exit gate tests for WRK-1035.

Tests are standalone — no mocking framework, no external deps beyond stdlib + PyYAML.
Run with: uv run --no-project python -m pytest scripts/work-queue/tests/test_stage1_gate.py -v
"""

import os
import tempfile
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Minimal implementation of check_stage1_capture_gate()
# ---------------------------------------------------------------------------

def check_stage1_capture_gate(evidence_dir: pathlib.Path) -> bool:
    """
    Returns True when user-review-capture.yaml is present and valid:
      - scope_approved is True (bool)
      - confirmed_at is a non-empty string
    Returns False otherwise (missing file, scope_approved=False, etc.).
    Route A n/a bypass: if n/a key is present and truthy, return True.
    """
    artifact = evidence_dir / "user-review-capture.yaml"
    if not artifact.exists():
        return False

    # Parse YAML without PyYAML dependency (basic key:value only)
    data = _parse_simple_yaml(artifact.read_text())

    # Route A n/a bypass
    na_val = data.get("n/a", "false")
    if str(na_val).strip().lower() in ("true", "yes", "1"):
        reason = data.get("n/a_reason", "").strip()
        return bool(reason)

    scope_approved = data.get("scope_approved", "false")
    if isinstance(scope_approved, bool):
        approved = scope_approved
    else:
        approved = str(scope_approved).strip().lower() in ("true", "yes", "1")

    confirmed_at = str(data.get("confirmed_at", "")).strip()
    return approved and bool(confirmed_at)


def _parse_simple_yaml(text: str) -> dict:
    """
    Minimal key: value YAML parser sufficient for the flat user-review-capture.yaml.
    Handles: string values, booleans (true/false), comments (#), empty values.
    """
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Strip inline comments
        if "#" in value:
            value = value[: value.index("#")].strip()
        # Parse booleans
        if value.lower() == "true":
            result[key] = True
        elif value.lower() == "false":
            result[key] = False
        else:
            result[key] = value
    return result


# ---------------------------------------------------------------------------
# T1: Stage 2 entry blocked when user-review-capture.yaml absent
# ---------------------------------------------------------------------------

def test_t1_stage2_blocked_when_artifact_absent():
    """T1: Gate returns False when the artifact file does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_dir = pathlib.Path(tmpdir)
        # Do NOT create the artifact
        result = check_stage1_capture_gate(evidence_dir)
    assert result is False, "Gate must return False when artifact is absent"


# ---------------------------------------------------------------------------
# T2: Stage 2 entry passes when scope_approved: true and confirmed_at non-empty
# ---------------------------------------------------------------------------

def test_t2_stage2_passes_when_scope_approved_and_confirmed_at_set():
    """T2: Gate returns True when scope_approved=true and confirmed_at is an ISO datetime."""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_dir = pathlib.Path(tmpdir)
        artifact = evidence_dir / "user-review-capture.yaml"
        artifact.write_text(
            "stage: 1\n"
            "wrk_id: WRK-1035\n"
            "reviewer: vamsee\n"
            "confirmed_at: 2026-03-08T12:00:00Z\n"
            "scope_approved: true\n"
            "notes: Scope looks good\n"
        )
        result = check_stage1_capture_gate(evidence_dir)
    assert result is True, "Gate must return True when scope_approved=true and confirmed_at is set"


# ---------------------------------------------------------------------------
# T3: Stage 2 entry blocked when scope_approved: false
# ---------------------------------------------------------------------------

def test_t3_stage2_blocked_when_scope_approved_false():
    """T3: Gate returns False when scope_approved=false (user requested revision)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_dir = pathlib.Path(tmpdir)
        artifact = evidence_dir / "user-review-capture.yaml"
        artifact.write_text(
            "stage: 1\n"
            "wrk_id: WRK-1035\n"
            "reviewer: vamsee\n"
            "confirmed_at: 2026-03-08T12:00:00Z\n"
            "scope_approved: false\n"
            "notes: Needs revision\n"
        )
        result = check_stage1_capture_gate(evidence_dir)
    assert result is False, "Gate must return False when scope_approved=false"


# ---------------------------------------------------------------------------
# T4: Template file at specs/templates/user-review-capture.yaml has all required fields
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"stage", "wrk_id", "reviewer", "confirmed_at", "scope_approved", "notes"}

def test_t4_template_has_all_required_fields():
    """T4: The template file contains all required fields."""
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    template_path = repo_root / "specs" / "templates" / "user-review-capture.yaml"
    assert template_path.exists(), f"Template not found at {template_path}"

    data = _parse_simple_yaml(template_path.read_text())
    present_fields = set(data.keys())

    missing = REQUIRED_FIELDS - present_fields
    assert not missing, (
        f"Template is missing required fields: {missing}. "
        f"Present fields: {present_fields}"
    )
