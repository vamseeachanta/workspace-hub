"""Tests for scripts/gtm/prospect_adapter.py — scaffolding layer.

Covers:
  1. Load + validate a well-formed intake that uses canonical_ref=seven-borealis.
  2. Load + validate a well-formed demo_04 intake that uses canonical_ref=pipelay-barge.
  3. Reject a demo_04 intake that points at a wrong-shape canonical YAML.
  4. Malformed YAML raises ProspectIntakeError.
  5. Q6 rejection: demo_01 + vessel block is rejected.
  6. Q6 rejection: demo_03 without vessel block is rejected.
  7. Demo_04 materialization writes the expected data files and optional env override.
  8. Non-demo_04 materialization paths + run_demo remain explicit stubs.
"""
from __future__ import annotations

import json
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


def _valid_demo_04_canonical_pipelay_yaml() -> str:
    """Demo_04 intake that references the canonical pipelay-barge vessel."""
    return """\
prospect:
  company: "Bluewater Pipelines"
  contact: "ops@bluewater.example"
  nda_in_place: true
  target_demo: "demo_04"
  delivery_deadline_utc: "2026-04-22T17:00Z"
vessel:
  shape: "pipelay"
  source: "canonical_ref"
  canonical_ref: "pipelay-barge"
structure:
  kind: "pipeline"
  body:
    outer_diameter_m: 0.3239
    wall_thickness_m: 0.0191
    material: "X65"
output:
  brand_header: "Prepared for Bluewater Pipelines"
  brand_footer: "Confidential - NDA"
  publish_private_url: false
"""


def _demo_04_with_wrong_canonical_yaml() -> str:
    """Demo_04 intake that incorrectly points to a csv_hlv canonical vessel."""
    return """\
prospect:
  company: "Bluewater Pipelines"
  contact: "ops@bluewater.example"
  nda_in_place: true
  target_demo: "demo_04"
  delivery_deadline_utc: "2026-04-22T17:00Z"
vessel:
  shape: "pipelay"
  source: "canonical_ref"
  canonical_ref: "seven-borealis"
structure:
  kind: "pipeline"
  body:
    outer_diameter_m: 0.3239
    wall_thickness_m: 0.0191
    material: "X65"
output:
  brand_header: "Prepared for Bluewater Pipelines"
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


def test_load_and_validate_accepts_canonical_pipelay_barge_for_demo_04(
    tmp_path: Path,
) -> None:
    intake_file = tmp_path / "bluewater-demo04.yaml"
    intake_file.write_text(_valid_demo_04_canonical_pipelay_yaml(), encoding="utf-8")

    result = load_and_validate(intake_file)

    assert isinstance(result, ProspectInput)
    assert result.target_demo == "demo_04"
    assert result.vessel_shape == "pipelay"
    assert result.structure_kind == "pipeline"
    assert result.company == "Bluewater Pipelines"
    assert result.contact == "ops@bluewater.example"
    assert result.source_path == intake_file


def test_load_and_validate_rejects_demo_04_when_canonical_ref_has_wrong_shape(
    tmp_path: Path,
) -> None:
    intake_file = tmp_path / "wrong-canonical-demo04.yaml"
    intake_file.write_text(_demo_04_with_wrong_canonical_yaml(), encoding="utf-8")

    with pytest.raises(ProspectIntakeError, match=r"canonical vessel.*pipelay"):
        load_and_validate(intake_file)


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


def test_materialize_demo_04_writes_pipelay_vessels_and_pipeline_files(
    tmp_path: Path,
) -> None:
    intake_file = tmp_path / "bluewater-demo04.yaml"
    intake_file.write_text(_valid_demo_04_canonical_pipelay_yaml(), encoding="utf-8")
    prospect = load_and_validate(intake_file)

    bundle = materialize_demo_inputs(prospect, tmp_path)

    assert isinstance(bundle, DemoInputBundle)
    assert bundle.demo_id == "demo_04"
    assert bundle.data_dir == tmp_path / "data"
    assert bundle.vessel_file == bundle.data_dir / "pipelay_vessels.json"
    assert bundle.structure_file == bundle.data_dir / "pipelines.json"
    assert bundle.vessel_file.exists()
    assert bundle.structure_file.exists()
    vessel_payload = json.loads(bundle.vessel_file.read_text(encoding="utf-8"))
    assert vessel_payload["vessels"][0]["id"] == "pipelay-barge"
    assert vessel_payload["vessels"][0]["pipelay_system"]["method"] == "S-lay"
    structure_payload = json.loads(bundle.structure_file.read_text(encoding="utf-8"))
    assert structure_payload["pipes"][0]["outer_diameter_m"] == pytest.approx(0.3239)
    assert structure_payload["pipes"][0]["wall_thickness_m"] == pytest.approx(0.0191)


def test_materialize_demo_04_writes_environment_override_when_present(
    tmp_path: Path,
) -> None:
    intake_file = tmp_path / "bluewater-demo04-env.yaml"
    intake_file.write_text(
        _valid_demo_04_canonical_pipelay_yaml().replace(
            'structure:\n',
            'environment:\n  water_depths_m: [50, 75]\n  hs_values_m: [1.0, 1.5]\n  current_velocity_ms: 0.4\nstructure:\n',
        ),
        encoding="utf-8",
    )
    prospect = load_and_validate(intake_file)

    bundle = materialize_demo_inputs(prospect, tmp_path)

    assert bundle.env_override_path == bundle.data_dir / "prospect_env.json"
    assert bundle.env_override_path.exists()
    env_payload = json.loads(bundle.env_override_path.read_text(encoding="utf-8"))
    assert env_payload["water_depths_m"] == [50, 75]
    assert env_payload["hs_values_m"] == [1.0, 1.5]
    assert env_payload["current_velocity_ms"] == pytest.approx(0.4)


def test_materialize_demo_inputs_is_a_wired_stub_for_unimplemented_demo(tmp_path: Path) -> None:
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
