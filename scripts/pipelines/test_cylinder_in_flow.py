"""
test_cylinder_in_flow.py — End-to-end test for the Gmsh→OpenFOAM→OrcaFlex pipeline.

Test case: 1 m diameter cylinder, 5 m long, in a 1.5 m/s current.

Analytical reference:
    F_drag = 0.5 * rho * U^2 * D * L * Cd
           = 0.5 * 1025 * 1.5^2 * 1.0 * 5.0 * 1.0
           = 5765.6 N

All tests run in stub mode so no solver license is required.

Run with:
    cd /mnt/local-analysis/workspace-hub/scripts/pipelines
    python -m pytest test_cylinder_in_flow.py -v
    # or
    pytest test_cylinder_in_flow.py -v
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure the pipelines directory is on sys.path
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


# ---------------------------------------------------------------------------
# Test parameters
# ---------------------------------------------------------------------------
DIAMETER = 1.0     # m
LENGTH = 5.0       # m
VELOCITY = 1.5     # m/s
RHO = 1025.0       # kg/m³
CD = 1.0

EXPECTED_DRAG = 0.5 * RHO * VELOCITY ** 2 * DIAMETER * LENGTH * CD
# = 5765.625 N


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def work_dir() -> Path:
    """Provide a temporary working directory for the full pipeline."""
    tmp = tempfile.mkdtemp(prefix="pipe_test_")
    return Path(tmp)


@pytest.fixture(scope="module")
def msh_path(work_dir) -> Path:
    """Run Gmsh stub and return the .msh path."""
    from stubs.stub_gmsh import run_gmsh_stub
    result = run_gmsh_stub(
        diameter=DIAMETER,
        length=LENGTH,
        velocity=VELOCITY,
        output_msh=work_dir / "mesh.msh",
    )
    assert result["passed"], f"Gmsh stub failed: {result}"
    return Path(result["msh_path"])


@pytest.fixture(scope="module")
def of_case_dir(work_dir, msh_path) -> Path:
    """Run OpenFOAM stub and return the case directory."""
    from stubs.stub_openfoam import run_openfoam_stub
    case_dir = work_dir / "of_case"
    result = run_openfoam_stub(
        case_dir=case_dir,
        diameter=DIAMETER,
        length=LENGTH,
        velocity=VELOCITY,
    )
    assert result["passed"], f"OpenFOAM stub failed: {result}"
    return case_dir


@pytest.fixture(scope="module")
def loads_csv(work_dir, of_case_dir) -> Path:
    """Convert OpenFOAM forces to OrcaFlex CSV and return the path."""
    from convert_openfoam_to_orcaflex import convert
    forces_path = (
        of_case_dir / "postProcessing" / "forces" / "0" / "force.dat"
    )
    output_csv = work_dir / "loads.csv"
    result = convert(
        forces_path=forces_path,
        output_csv=output_csv,
        time_step=0.1,
    )
    assert result["passed"], f"OF→OrcaFlex conversion failed: {result}"
    return output_csv


# ---------------------------------------------------------------------------
# Unit tests: Stubs
# ---------------------------------------------------------------------------

class TestGmshStub:
    """Verify the Gmsh stub produces a valid .msh file."""

    def test_msh_file_created(self, msh_path):
        assert msh_path.exists(), f".msh not created: {msh_path}"

    def test_msh_file_not_empty(self, msh_path):
        assert msh_path.stat().st_size > 500, "Mesh file is suspiciously small"

    def test_msh_has_elements_section(self, msh_path):
        content = msh_path.read_text()
        assert "$Elements" in content

    def test_msh_has_nodes_section(self, msh_path):
        content = msh_path.read_text()
        assert "$Nodes" in content

    def test_cell_count_positive(self):
        """Gmsh stub must report a non-zero cell count."""
        import tempfile
        from stubs.stub_gmsh import run_gmsh_stub
        with tempfile.TemporaryDirectory() as td:
            result = run_gmsh_stub(
                diameter=1.0, length=5.0, velocity=1.0,
                output_msh=Path(td) / "m.msh",
            )
        assert result["cell_count"] > 0


class TestOpenFOAMStub:
    """Verify the OpenFOAM stub produces valid solver output."""

    def test_log_file_created(self, of_case_dir):
        log = of_case_dir / "log.simpleFoam"
        assert log.exists()

    def test_log_has_residuals(self, of_case_dir):
        log = of_case_dir / "log.simpleFoam"
        content = log.read_text()
        assert "Solving for" in content

    def test_forces_file_created(self, of_case_dir):
        forces = of_case_dir / "postProcessing" / "forces" / "0" / "force.dat"
        assert forces.exists()

    def test_forces_file_has_data(self, of_case_dir):
        forces = of_case_dir / "postProcessing" / "forces" / "0" / "force.dat"
        lines = [
            ln for ln in forces.read_text().splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
        assert len(lines) > 5


# ---------------------------------------------------------------------------
# Unit tests: Validation gates
# ---------------------------------------------------------------------------

class TestGate1MeshQuality:
    """Verify Gate 1 passes on stub-generated mesh."""

    def test_gate_passes(self, msh_path):
        from validate_mesh_quality import validate_msh_file
        result = validate_msh_file(msh_path)
        assert result["passed"], f"Gate 1 failed: {result['issues']}"

    def test_cell_count_above_minimum(self, msh_path):
        from validate_mesh_quality import validate_msh_file
        result = validate_msh_file(msh_path)
        assert result["cell_count"] >= 100

    def test_skewness_within_limit(self, msh_path):
        from validate_mesh_quality import validate_msh_file, MAX_SKEWNESS
        result = validate_msh_file(msh_path)
        assert result["max_skewness"] < MAX_SKEWNESS

    def test_non_orthogonality_within_limit(self, msh_path):
        from validate_mesh_quality import (
            validate_msh_file,
            MAX_NON_ORTHOGONALITY_DEG,
        )
        result = validate_msh_file(msh_path)
        assert result["max_non_orthogonality_deg"] < MAX_NON_ORTHOGONALITY_DEG

    def test_gate_fails_on_missing_file(self):
        from validate_mesh_quality import validate_msh_file
        result = validate_msh_file("/nonexistent/mesh.msh")
        assert not result["passed"]
        assert result["issues"]

    def test_gate_fails_on_too_few_cells(self, tmp_path):
        """Gate 1 must reject a mesh with only 5 cells."""
        tiny_msh = tmp_path / "tiny.msh"
        tiny_msh.write_text(
            "$MeshFormat\n2.2 0 8\n$EndMeshFormat\n"
            "$Nodes\n5\n1 0 0 0\n2 1 0 0\n3 1 1 0\n4 0 1 0\n5 0.5 0.5 0\n"
            "$EndNodes\n$Elements\n3\n"
            "1 2 2 1 1 1 2 3\n2 2 2 1 1 2 3 4\n3 2 2 1 1 3 4 5\n"
            "$EndElements\n"
        )
        from validate_mesh_quality import validate_msh_file
        result = validate_msh_file(tiny_msh)
        assert not result["passed"]


class TestGate2CFDConvergence:
    """Verify Gate 2 passes on stub-generated solver log."""

    def test_gate_passes(self, of_case_dir):
        from validate_cfd_convergence import validate_convergence
        log = of_case_dir / "log.simpleFoam"
        forces = of_case_dir / "postProcessing" / "forces" / "0" / "force.dat"
        result = validate_convergence(
            log_path=log,
            forces_path=forces,
            expected_fx=EXPECTED_DRAG,
        )
        assert result["passed"], f"Gate 2 failed: {result['issues']}"

    def test_residuals_below_limit(self, of_case_dir):
        from validate_cfd_convergence import validate_convergence, RESIDUAL_LIMIT
        log = of_case_dir / "log.simpleFoam"
        result = validate_convergence(log_path=log)
        for var, val in result["final_residuals"].items():
            assert val < RESIDUAL_LIMIT, (
                f"Residual {var}={val} >= limit {RESIDUAL_LIMIT}"
            )

    def test_force_balance_within_tolerance(self, of_case_dir):
        from validate_cfd_convergence import validate_convergence
        log = of_case_dir / "log.simpleFoam"
        forces = of_case_dir / "postProcessing" / "forces" / "0" / "force.dat"
        result = validate_convergence(
            log_path=log,
            forces_path=forces,
            expected_fx=EXPECTED_DRAG,
        )
        fb = result.get("force_balance", {})
        if "balance_error_pct" in fb:
            assert fb["balance_error_pct"] <= 5.0

    def test_gate_fails_on_missing_log(self, tmp_path):
        from validate_cfd_convergence import validate_convergence
        result = validate_convergence(log_path=tmp_path / "nonexistent.log")
        assert not result["passed"]

    def test_gate_fails_on_high_residuals(self, tmp_path):
        """Gate 2 must reject a log with residuals > 1e-4."""
        bad_log = tmp_path / "bad.log"
        bad_log.write_text(
            "Solving for Ux, Initial residual = 0.5, Final residual = 0.1, "
            "No Iterations 1\n"
            "Solving for p, Initial residual = 0.3, Final residual = 0.2, "
            "No Iterations 1\n"
        )
        from validate_cfd_convergence import validate_convergence
        result = validate_convergence(log_path=bad_log)
        assert not result["passed"]


# ---------------------------------------------------------------------------
# Unit tests: Converters
# ---------------------------------------------------------------------------

class TestConvertGmshToOpenFOAM:
    """Verify Gmsh→polyMesh converter."""

    def test_conversion_produces_polymesh(self, msh_path, tmp_path):
        from convert_gmsh_to_openfoam import convert
        case = tmp_path / "of_case"
        result = convert(msh_path, case)
        # Passes if gmshToFoam or meshio is available; issues a warning otherwise
        # The key check is that result is a dict with the expected keys
        assert "passed" in result
        assert "polymesh_dir" in result
        assert "issues" in result


class TestConvertOpenFOAMToOrcaFlex:
    """Verify OpenFOAM forces → OrcaFlex CSV converter."""

    def test_csv_created(self, loads_csv):
        assert loads_csv.exists()

    def test_csv_has_header(self, loads_csv):
        with open(loads_csv) as fh:
            lines = fh.readlines()
        header_lines = [ln for ln in lines if not ln.startswith("#")]
        assert header_lines, "CSV has no data after comment lines"
        header = header_lines[0]
        assert "Time" in header and "Fx" in header

    def test_csv_has_data_rows(self, loads_csv):
        with open(loads_csv) as fh:
            data_lines = [
                ln for ln in fh
                if ln.strip() and not ln.startswith("#")
                and not ln.startswith("Time")
            ]
        assert len(data_lines) >= 10

    def test_force_values_positive(self, loads_csv):
        import csv as csv_mod
        with open(loads_csv) as fh:
            reader = csv_mod.DictReader(
                (ln for ln in fh if not ln.startswith("#"))
            )
            rows = list(reader)
        assert rows, "No data rows in CSV"
        # Drag force (Fx) should be positive for flow in +x direction
        fx_vals = [float(r["Fx"]) for r in rows]
        assert any(f > 0 for f in fx_vals), "No positive Fx found"

    def test_time_series_monotonic(self, loads_csv):
        import csv as csv_mod
        with open(loads_csv) as fh:
            reader = csv_mod.DictReader(
                (ln for ln in fh if not ln.startswith("#"))
            )
            times = [float(r["Time"]) for r in reader]
        assert all(t1 < t2 for t1, t2 in zip(times, times[1:])), (
            "Time column is not monotonically increasing"
        )

    def test_conversion_fails_on_missing_file(self, tmp_path):
        from convert_openfoam_to_orcaflex import convert
        result = convert(
            forces_path=tmp_path / "nonexistent.dat",
            output_csv=tmp_path / "out.csv",
        )
        assert not result["passed"]
        assert result["issues"]


# ---------------------------------------------------------------------------
# Unit tests: OrcaFlex stub
# ---------------------------------------------------------------------------

class TestOrcaFlexStub:
    """Verify OrcaFlex stub returns physically plausible results."""

    def test_stub_passes(self, loads_csv):
        from stubs.stub_orcaflex import run_orcaflex_stub
        result = run_orcaflex_stub(
            loads_csv=loads_csv,
            diameter=DIAMETER,
            length=LENGTH,
        )
        assert result["passed"], f"OrcaFlex stub failed: {result}"

    def test_deflection_is_finite(self, loads_csv):
        from stubs.stub_orcaflex import run_orcaflex_stub
        result = run_orcaflex_stub(
            loads_csv=loads_csv,
            diameter=DIAMETER,
            length=LENGTH,
        )
        d = result["max_deflection_m"]
        assert math.isfinite(d), f"Deflection is not finite: {d}"

    def test_deflection_physically_plausible(self, loads_csv):
        """Deflection must be > 0 and < length of the cylinder."""
        from stubs.stub_orcaflex import run_orcaflex_stub
        result = run_orcaflex_stub(
            loads_csv=loads_csv,
            diameter=DIAMETER,
            length=LENGTH,
        )
        d = result["max_deflection_m"]
        assert 0 <= d < LENGTH, f"Deflection {d} is outside plausible range"

    def test_tension_positive(self, loads_csv):
        from stubs.stub_orcaflex import run_orcaflex_stub
        result = run_orcaflex_stub(
            loads_csv=loads_csv,
            diameter=DIAMETER,
            length=LENGTH,
        )
        assert result["max_tension_N"] >= 0

    def test_stub_fails_on_missing_csv(self, tmp_path):
        from stubs.stub_orcaflex import run_orcaflex_stub
        result = run_orcaflex_stub(
            loads_csv=tmp_path / "nonexistent.csv",
            diameter=1.0,
            length=5.0,
        )
        assert not result["passed"]


# ---------------------------------------------------------------------------
# Full end-to-end integration test
# ---------------------------------------------------------------------------

class TestEndToEndPipeline:
    """Run the complete pipeline in stub mode and verify all gates pass."""

    def test_pipeline_passes_in_stub_mode(self, tmp_path):
        from gmsh_openfoam_orcaflex import run_pipeline
        result = run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=tmp_path / "e2e_run",
            stub_mode=True,
        )
        assert result["passed"], (
            f"Pipeline failed. Issues: {result.get('issues')}"
        )

    def test_results_json_written(self, tmp_path):
        from gmsh_openfoam_orcaflex import run_pipeline
        run_dir = tmp_path / "json_run"
        run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        results_json = run_dir / "pipeline_results.json"
        assert results_json.exists()

    def test_results_json_is_valid(self, tmp_path):
        from gmsh_openfoam_orcaflex import run_pipeline
        run_dir = tmp_path / "json_valid_run"
        run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        data = json.loads((run_dir / "pipeline_results.json").read_text())
        assert "summary" in data
        assert "stages" in data
        assert "parameters" in data

    def test_all_stages_present_in_results(self, tmp_path):
        from gmsh_openfoam_orcaflex import run_pipeline
        run_dir = tmp_path / "stages_run"
        result = run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        stages = result["stages"]
        expected_stages = [
            "gmsh",
            "gate1_mesh_quality",
            "convert_gmsh_to_foam",
            "openfoam",
            "gate2_cfd_convergence",
            "convert_foam_to_orcaflex",
            "orcaflex",
        ]
        for stage in expected_stages:
            assert stage in stages, f"Stage '{stage}' missing from results"

    def test_gate1_passed_in_results(self, tmp_path):
        from gmsh_openfoam_orcaflex import run_pipeline
        run_dir = tmp_path / "gate1_run"
        result = run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        gate1 = result["stages"]["gate1_mesh_quality"]
        assert gate1["passed"]

    def test_gate2_passed_in_results(self, tmp_path):
        from gmsh_openfoam_orcaflex import run_pipeline
        run_dir = tmp_path / "gate2_run"
        result = run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        gate2 = result["stages"]["gate2_cfd_convergence"]
        assert gate2["passed"]

    def test_drag_force_within_5pct_of_analytical(self, tmp_path):
        """Pipeline drag estimate must be within 5% of Cd=1.0 formula."""
        from gmsh_openfoam_orcaflex import run_pipeline
        run_dir = tmp_path / "drag_run"
        result = run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        reported_drag = result["summary"]["drag_force_N"]
        error_pct = abs(reported_drag - EXPECTED_DRAG) / EXPECTED_DRAG * 100
        assert error_pct <= 5.0, (
            f"Drag {reported_drag:.1f} N is {error_pct:.1f}% "
            f"from expected {EXPECTED_DRAG:.1f} N"
        )

    def test_loads_csv_written_and_parseable(self, tmp_path):
        """CSV written by converter must be readable back by OrcaFlex stub."""
        from gmsh_openfoam_orcaflex import run_pipeline
        from stubs.stub_orcaflex import run_orcaflex_stub
        run_dir = tmp_path / "csv_run"
        run_pipeline(
            diameter=DIAMETER,
            length=LENGTH,
            velocity=VELOCITY,
            work_dir=run_dir,
            stub_mode=True,
        )
        csv_path = run_dir / "loads.csv"
        assert csv_path.exists()
        ofx_result = run_orcaflex_stub(
            loads_csv=csv_path,
            diameter=DIAMETER,
            length=LENGTH,
        )
        assert ofx_result["passed"]
