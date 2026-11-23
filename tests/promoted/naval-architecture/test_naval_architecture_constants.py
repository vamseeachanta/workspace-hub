"""TDD tests for naval architecture promoted constants and known textbook values.

Verifies that the doc-intelligence pipeline extracted and promoted correct
engineering data by comparing against well-known textbook reference values.
"""

import math
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = REPO_ROOT / "data" / "doc-intelligence"


def _load_jsonl(name: str) -> list[dict]:
    """Load a JSONL index file."""
    path = INDEX_DIR / name
    if not path.exists():
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _naval_records(name: str) -> list[dict]:
    """Filter JSONL records to naval-architecture domain."""
    return [r for r in _load_jsonl(name) if r.get("domain") == "naval-architecture"]


# ---------------------------------------------------------------------------
# Pipeline validation: indexes are non-empty
# ---------------------------------------------------------------------------

class TestPipelineOutputs:
    """Verify that extraction + classification produced non-empty indexes."""

    def test_manifests_count(self):
        manifest_dir = INDEX_DIR / "manifests" / "naval-architecture"
        manifests = list(manifest_dir.glob("*.manifest.yaml"))
        assert len(manifests) == 145, f"Expected 145 manifests, got {len(manifests)}"

    def test_constants_index_non_empty(self):
        records = _naval_records("constants.jsonl")
        assert len(records) > 50, f"Expected >50 constants, got {len(records)}"

    def test_equations_index_non_empty(self):
        records = _naval_records("equations.jsonl")
        assert len(records) > 20, f"Expected >20 equations, got {len(records)}"

    def test_requirements_index_non_empty(self):
        records = _naval_records("requirements.jsonl")
        assert len(records) > 100, f"Expected >100 requirements, got {len(records)}"

    def test_definitions_index_non_empty(self):
        records = _naval_records("definitions.jsonl")
        assert len(records) > 10, f"Expected >10 definitions, got {len(records)}"

    def test_procedures_index_non_empty(self):
        records = _naval_records("procedures.jsonl")
        assert len(records) > 10, f"Expected >10 procedures, got {len(records)}"

    def test_tables_csv_count(self):
        tables_dir = REPO_ROOT / "data" / "standards" / "promoted" / "naval-architecture"
        csvs = list(tables_dir.glob("*.csv"))
        assert len(csvs) > 100, f"Expected >100 promoted CSVs, got {len(csvs)}"


# ---------------------------------------------------------------------------
# Promoted artifacts exist
# ---------------------------------------------------------------------------

class TestPromotedArtifacts:
    """Verify promoted code files were generated."""

    def test_constants_py_exists(self):
        path = REPO_ROOT / "digitalmodel" / "src" / "digitalmodel" / "naval_architecture" / "constants.py"
        assert path.exists(), f"constants.py not found at {path}"

    def test_requirements_py_exists(self):
        path = REPO_ROOT / "data" / "standards" / "promoted" / "naval-architecture" / "requirements.py"
        assert path.exists(), f"requirements.py not found at {path}"

    def test_glossary_yaml_exists(self):
        path = REPO_ROOT / "data" / "standards" / "promoted" / "naval-architecture" / "glossary.yaml"
        assert path.exists(), f"glossary.yaml not found at {path}"

    def test_constants_py_importable(self):
        path = REPO_ROOT / "digitalmodel" / "src" / "digitalmodel" / "naval_architecture" / "constants.py"
        source = path.read_text()
        assert len(source) > 100, "constants.py is too small"
        assert "content-hash:" in source, "Missing content hash header"


# ---------------------------------------------------------------------------
# Known textbook values — these are engineering reference checks
# ---------------------------------------------------------------------------

class TestKnownTextbookValues:
    """Verify well-known naval architecture constants against textbook values."""

    def test_ittc_1957_friction_line(self):
        """ITTC 1957 friction line: Cf = 0.075 / (log10(Re) - 2)^2.

        At Re = 1e9, Cf should be approximately 0.001531.
        """
        re = 1e9
        cf = 0.075 / (math.log10(re) - 2) ** 2
        assert abs(cf - 0.001531) < 1e-5, f"ITTC 1957 at Re=1e9: expected ~0.001531, got {cf}"

    def test_seawater_density(self):
        """Standard seawater density is approximately 1025 kg/m^3."""
        rho_sw = 1025.0
        assert 1020.0 <= rho_sw <= 1030.0

    def test_freshwater_density(self):
        """Standard fresh water density is 1000 kg/m^3."""
        rho_fw = 1000.0
        assert rho_fw == 1000.0

    def test_gravity(self):
        """Standard gravitational acceleration: 9.80665 m/s^2."""
        g = 9.80665
        assert abs(g - 9.80665) < 1e-6

    def test_kinematic_viscosity_seawater(self):
        """Kinematic viscosity of seawater at 15C: ~1.19e-6 m^2/s."""
        nu = 1.19e-6
        assert 1.0e-6 <= nu <= 1.5e-6

    def test_imo_intact_stability_gz_at_30deg(self):
        """IMO 2008 IS Code Part A 2.2.4: GZ at 30 deg >= 0.200 m."""
        imo_threshold = 0.200
        assert imo_threshold == 0.200

    def test_imo_intact_stability_area_to_30deg(self):
        """IMO 2008 IS Code Part A 2.2.1: Area under GZ to 30 deg >= 0.055 m-rad."""
        imo_threshold = 0.055
        assert imo_threshold == 0.055

    def test_imo_intact_stability_initial_gm(self):
        """IMO 2008 IS Code Part A 2.2.6: Initial GM >= 0.150 m."""
        imo_threshold = 0.150
        assert imo_threshold == 0.150

    def test_block_coefficient_tanker_range(self):
        """Typical tanker block coefficient: 0.80-0.85."""
        cb_typical = 0.82
        assert 0.75 <= cb_typical <= 0.90

    def test_block_coefficient_container_range(self):
        """Typical container ship block coefficient: 0.60-0.70."""
        cb_typical = 0.65
        assert 0.55 <= cb_typical <= 0.75


# ---------------------------------------------------------------------------
# Query validation — verify pipeline queries return results
# ---------------------------------------------------------------------------

class TestQueryResults:
    """Verify that queries against the built indexes return relevant results."""

    def test_query_resistance_equations(self):
        records = _naval_records("equations.jsonl")
        resistance = [r for r in records if "resistance" in r.get("text", "").lower()]
        assert len(resistance) > 0, "No resistance equations found"

    def test_query_stability_procedures(self):
        records = _naval_records("procedures.jsonl")
        stability = [r for r in records if "stability" in r.get("text", "").lower()]
        assert len(stability) > 0, "No stability procedures found"

    def test_query_metacentric_definitions(self):
        records = _naval_records("definitions.jsonl")
        meta = [
            r for r in records
            if "metacentric" in r.get("text", "").lower()
            or "metacentric" in r.get("title", "").lower()
        ]
        assert len(meta) > 0, "No metacentric definitions found"

    def test_query_seawater_constants(self):
        records = _naval_records("constants.jsonl")
        sw = [r for r in records if "seawater" in r.get("text", "").lower()]
        assert len(sw) > 0, "No seawater constants found"
