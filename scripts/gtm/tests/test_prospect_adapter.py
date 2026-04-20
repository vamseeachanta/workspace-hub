"""Tests for scripts/gtm/prospect_adapter.py — scaffolding layer.

Covers:
  1. Load + validate a well-formed intake that uses canonical_ref=seven-borealis.
  2. Malformed YAML raises ProspectIntakeError.
  3. Q6 rejection: demo_01 + vessel block is rejected.
  4. Q6 rejection: demo_03 without vessel block is rejected.
  5. materialize_demo_inputs + run_demo raise NotImplementedError (interface wired).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from gtm.prospect_adapter import (  # noqa: E402  — sys.path tweak above
    DemoInputBundle,
    ProspectIntakeError,
    ProspectInput,
    load_and_validate,
    materialize_demo_inputs,
    run_demo,
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _valid_demo_05_intake_yaml() -> str:
    """Demo_05 intake that references the canonical seven-borealis vessel."""
    return """\
prospect:
  company: "Acme Marine Contractors"
  contact: "jane.doe@acme.example"
  nda_in_place: true
  target_demo: "demo_05"
  delivery_deadline_utc: "2026-04-21T17:00Z"
vessel:
  shape: "csv_hlv"
  source: "canonical_ref"
  canonical_ref: "seven-borealis"
structure:
  kind: "rigid_jumper"
  body:
    outer_diameter_m: 0.3239
    wall_thickness_m: 0.0254
    length_m: 45.0
    material: "X65"
environment:
  water_depths_m: [1500, 2000, 2500]
  hs_values_m: [1.5, 2.0, 2.5]
  current_velocity_ms: 0.5
output:
  brand_header: "Prepared for Acme Marine"
  brand_footer: "Confidential - NDA"
  publish_private_url: true
  gating: "hash"
  purge_after_utc: "2026-05-20T00:00Z"
"""


def _demo_01_with_vessel_yaml() -> str:
    """Demo_01 intake that (incorrectly) includes a vessel block — Q6 violation."""
    return """\
prospect:
  company: "Acme Marine Contractors"
  contact: "jane.doe@acme.example"
  nda_in_place: true
  target_demo: "demo_01"
  delivery_deadline_utc: "2026-04-21T17:00Z"
vessel:
  shape: "csv_hlv"
  source: "canonical_ref"
  canonical_ref: "seven-borealis"
structure:
  kind: "pipeline"
  body:
    outer_diameter_m: 0.3239
    wall_thickness_m: 0.0254
output:
  brand_header: "Prepared for Acme Marine"
  brand_footer: "Confidential - NDA"
  publish_private_url: false
"""


def _demo_03_without_vessel_yaml() -> str:
    """Demo_03 intake missing the vessel block — Q6 violation (conditional-required)."""
    return """\
prospect:
  company: "Acme Marine Contractors"
  contact: "jane.doe@acme.example"
  nda_in_place: true
  target_demo: "demo_03"
  delivery_deadline_utc: "2026-04-21T17:00Z"
structure:
  kind: "mudmat"
  body:
    plan_area_m2: 120.0
output:
  brand_header: "Prepared for Acme Marine"
  brand_footer: "Confidential - NDA"
  publish_private_url: false
"""


def _malformed_yaml() -> str:
    """Syntactically broken YAML (unclosed mapping)."""
    return "prospect:\n  company: \"Acme\n  contact: jane.doe@acme.example\n"


# ---------------------------------------------------------------------------
# Test 1: Happy path — demo_05 + canonical Seven Borealis reference.
# ---------------------------------------------------------------------------


def test_load_and_validate_accepts_canonical_seven_borealis_intake(tmp_path: Path) -> None:
    intake_file = tmp_path / "acme-demo05.yaml"
    intake_file.write_text(_valid_demo_05_intake_yaml(), encoding="utf-8")

    result = load_and_validate(intake_file)

    assert isinstance(result, ProspectInput)
    assert result.target_demo == "demo_05"
    assert result.vessel_shape == "csv_hlv"
    assert result.structure_kind == "rigid_jumper"
    assert result.company == "Acme Marine Contractors"
    assert result.contact == "jane.doe@acme.example"
    assert result.source_path == intake_file


# ---------------------------------------------------------------------------
# Test 2: Malformed YAML raises ProspectIntakeError.
# ---------------------------------------------------------------------------


def test_load_and_validate_rejects_malformed_yaml(tmp_path: Path) -> None:
    intake_file = tmp_path / "broken.yaml"
    intake_file.write_text(_malformed_yaml(), encoding="utf-8")

    with pytest.raises(ProspectIntakeError, match=r"(?i)malformed YAML"):
        load_and_validate(intake_file)


# ---------------------------------------------------------------------------
# Test 3: Q6 conditional — demo_01 + vessel block is rejected.
# ---------------------------------------------------------------------------


def test_load_and_validate_rejects_demo_01_with_vessel(tmp_path: Path) -> None:
    intake_file = tmp_path / "bad-demo01.yaml"
    intake_file.write_text(_demo_01_with_vessel_yaml(), encoding="utf-8")

    with pytest.raises(ProspectIntakeError):
        load_and_validate(intake_file)


# ---------------------------------------------------------------------------
# Test 4: Q6 conditional — demo_03 without vessel block is rejected.
# ---------------------------------------------------------------------------


def test_load_and_validate_rejects_demo_03_without_vessel(tmp_path: Path) -> None:
    intake_file = tmp_path / "bad-demo03.yaml"
    intake_file.write_text(_demo_03_without_vessel_yaml(), encoding="utf-8")

    with pytest.raises(ProspectIntakeError):
        load_and_validate(intake_file)


# ---------------------------------------------------------------------------
# Test 5: Stubs raise NotImplementedError so downstream callers see an
# explicit signal rather than a silent success or AttributeError.
# ---------------------------------------------------------------------------


def test_materialize_demo_inputs_is_a_wired_stub(tmp_path: Path) -> None:
    intake_file = tmp_path / "acme-demo05.yaml"
    intake_file.write_text(_valid_demo_05_intake_yaml(), encoding="utf-8")
    prospect = load_and_validate(intake_file)

    with pytest.raises(NotImplementedError, match=r"materialize_demo_inputs"):
        materialize_demo_inputs(prospect, tmp_path)


def test_run_demo_is_a_wired_stub(tmp_path: Path) -> None:
    # Construct a DemoInputBundle directly (materialize is still a stub).
    bundle = DemoInputBundle(
        demo_id="demo_05",
        tmpdir=tmp_path,
        data_dir=tmp_path / "data",
    )
    with pytest.raises(NotImplementedError, match=r"run_demo"):
        run_demo(bundle, demo_id=5)
