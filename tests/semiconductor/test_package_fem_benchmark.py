"""Tests for #2511 semiconductor package FEM benchmark.

These tests intentionally define the public contract before implementation.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "semiconductor" / "package_fem_benchmark.py"


def load_module():
    spec = importlib.util.spec_from_file_location("package_fem_benchmark", MODULE_PATH)
    assert spec and spec.loader, f"module is importable from {MODULE_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_default_spec_uses_si_units_sources_and_required_layers():
    fem = load_module()
    spec = fem.build_default_spec()

    assert spec.units == "SI"
    assert spec.length_m > 0
    assert spec.width_m > 0
    layer_names = {layer.name for layer in spec.layers}
    assert {"substrate", "die", "mold", "solder_zone"}.issubset(layer_names)

    assert spec.materials
    for material in spec.materials.values():
        assert material.E_Pa > 0
        assert 0 <= material.nu < 0.5
        assert material.cte_per_K > 0
        assert material.k_W_m_K > 0
        assert material.source.strip()
        assert material.source_note.strip()


def test_structured_hex_mesh_counts_sets_and_material_assignment():
    fem = load_module()
    spec = fem.build_default_spec(nx=3, ny=2)
    mesh = fem.structured_hex_mesh(spec)

    nz = sum(layer.mesh_divisions_z for layer in spec.layers)
    assert len(mesh.nodes) == (spec.nx + 1) * (spec.ny + 1) * (nz + 1)
    assert len(mesh.elements) == spec.nx * spec.ny * nz
    assert {"top", "bottom", "die", "substrate"}.issubset(mesh.sets)
    assert mesh.sets["top"]
    assert mesh.sets["bottom"]

    layer_counts = {layer.name: 0 for layer in spec.layers}
    for element in mesh.elements:
        layer_counts[element.layer_name] += 1
        assert element.material_id in spec.materials
    assert all(count > 0 for count in layer_counts.values())


def test_package_stackup_svg_is_generated_and_nonempty(tmp_path):
    fem = load_module()
    spec = fem.build_default_spec()
    out = tmp_path / "artifacts"
    out.mkdir()
    path = fem.write_stackup_svg(spec, out)

    text = path.read_text(encoding="utf-8")
    assert path.name == "package_stackup.svg"
    assert "<svg" in text
    for label in ["substrate", "die", "mold", "solder_zone"]:
        assert label in text


def test_calculix_input_decks_include_materials_steps_units_and_output_cards(tmp_path):
    fem = load_module()
    spec = fem.build_default_spec(nx=2, ny=2)
    mesh = fem.structured_hex_mesh(spec)
    paths = fem.write_calculix_inputs(spec, mesh, tmp_path)

    assert {"thermal", "thermomechanical"}.issubset(paths)
    for path in paths.values():
        text = path.read_text(encoding="utf-8")
        assert "SI units" in text
        assert "*NODE" in text
        assert "*ELEMENT" in text
        assert "*MATERIAL" in text
        assert "*STEP" in text
        assert "*END STEP" in text
        assert ("*NODE FILE" in text or "*NODE PRINT" in text)
        assert ("*EL FILE" in text or "*EL PRINT" in text)
    thermal_text = paths["thermal"].read_text(encoding="utf-8")
    assert "*CONDUCTIVITY" in thermal_text
    assert "*DFLUX" in thermal_text
    assert "power_W=2" in thermal_text
    assert "*NSET, NSET=ALLNODES" in thermal_text
    assert "ALLNODES," in thermal_text
    assert "ALL_ELEMENTS," not in thermal_text
    mech_text = paths["thermomechanical"].read_text(encoding="utf-8")
    assert "*EXPANSION" in mech_text
    assert "*TEMPERATURE" in mech_text
    assert f"ALLNODES, {spec.junction_C:.3f}" not in mech_text
    assert "power-based 1D thermal-resistance profile" in mech_text
    assert "*NSET, NSET=ALLNODES" in mech_text
    assert "ALLNODES," in mech_text
    assert "ALL_ELEMENTS," not in mech_text


def test_power_based_temperature_profile_uses_cumulative_layer_resistance():
    fem = load_module()
    spec = fem.build_default_spec(nx=1, ny=1)
    mesh = fem.structured_hex_mesh(spec)
    temps = fem.node_temperature_map(spec, mesh)
    area = spec.area_m2
    cumulative = 0.0
    expected_by_z = {0.0: spec.ambient_C}
    z = 0.0
    for layer in spec.layers:
        material = spec.materials[layer.material_id]
        cumulative += spec.power_W * layer.thickness_m / (material.k_W_m_K * area)
        z += layer.thickness_m
        expected_by_z[round(z, 12)] = spec.ambient_C + cumulative

    for z_key, expected in expected_by_z.items():
        matching = [node.id for node in mesh.nodes if round(node.z, 12) == z_key]
        assert matching, z_key
        for node_id in matching:
            assert temps[node_id] == pytest.approx(expected)


def test_cli_regenerates_expected_artifacts_manifest_summary_and_report(tmp_path):
    output = tmp_path / "package_fem_benchmark"
    report = tmp_path / "semiconductor-package-fem-benchmark.md"
    cmd = [
        sys.executable,
        str(MODULE_PATH),
        "--output",
        str(output),
        "--report",
        str(report),
        "--no-solver",
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    assert "wrote" in result.stdout.lower()

    expected = {
        "README.md",
        "package_thermal.inp",
        "package_thermomechanical.inp",
        "mesh_summary.csv",
        "result_profiles.csv",
        "benchmark_summary.json",
        "artifact_manifest.sha256",
        "package_stackup.svg",
        "temperature_profile.svg",
        "stress_warpage_estimates.svg",
    }
    assert expected.issubset({p.name for p in output.iterdir()})
    assert report.exists()

    summary = json.loads((output / "benchmark_summary.json").read_text(encoding="utf-8"))
    assert summary["units"] == "SI"
    assert summary["mesh"]["node_count"] > 0
    assert summary["mesh"]["element_count"] > 0
    sanity = summary["sanity_checks"]
    assert sanity["thermal_resistance_K_per_W"] > 0
    assert sanity["delta_T_K"] > 0
    assert sanity["max_free_strain"] > 0
    assert sanity["warpage_style_um"] >= 0
    assert summary["solver_status"]["status"] == "skipped"
    assert summary["solver_status"]["reason"] == "no_solver_requested"
    assert set(summary["solver_status"]["decks"]) == {"thermal", "thermomechanical"}
    assert all(deck["status"] == "skipped" for deck in summary["solver_status"]["decks"].values())
    assert summary["materials"]
    assert all(m["source"] and m["source_note"] for m in summary["materials"].values())
    assert "artifact_hashes" in summary
    assert "temperature_profile.svg" in summary["artifact_hashes"]

    manifest = (output / "artifact_manifest.sha256").read_text(encoding="utf-8")
    for name in expected - {"artifact_manifest.sha256"}:
        assert name in manifest
    for line in manifest.splitlines():
        digest, name = line.split("  ", 1)
        path = (output / name).resolve()
        import hashlib

        assert path.exists(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

    rows = list(csv.DictReader((output / "result_profiles.csv").open(encoding="utf-8")))
    assert rows
    assert {"z_m", "temperature_C", "normalized_stress", "warpage_style_um"}.issubset(rows[0])

    report_text = report.read_text(encoding="utf-8")
    for phrase in [
        "Boundary Conditions",
        "Loads",
        "Materials and Provenance",
        "Solver Status",
        "temperature_profile.svg",
        "stress_warpage_estimates.svg",
        "![Temperature profile](",
        "Convergence and Smoke Checks",
        "| Check | Result |",
        "not production-certified",
        "not for production signoff",
    ]:
        assert phrase in report_text

    image_targets = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", report_text)
    assert image_targets
    for target in image_targets:
        assert (report.parent / target).resolve().exists(), target


def test_report_does_not_make_affirmative_jedec_or_ipc_compliance_claims(tmp_path):
    fem = load_module()
    output = tmp_path / "artifacts"
    report = tmp_path / "report.md"
    fem.main(["--output", str(output), "--report", str(report), "--no-solver"])
    text = report.read_text(encoding="utf-8")

    allowed_negative = [
        "not JEDEC-compliant",
        "not IPC-compliant",
        "not production-certified",
        "not validated to JEDEC",
        "not for production signoff",
    ]
    normalized = text
    for phrase in allowed_negative:
        normalized = normalized.replace(phrase, "")

    forbidden = [
        r"JEDEC[- ]?compliant",
        r"IPC[- ]?compliant",
        r"meets\s+JESD22",
        r"per\s+IPC",
        r"validated\s+to\s+JEDEC",
        r"\bcertified\b",
        r"production\s+signoff",
    ]
    for pattern in forbidden:
        assert not re.search(pattern, normalized, flags=re.IGNORECASE), pattern


def test_solver_wrapper_behaviors_and_mutually_exclusive_flags(monkeypatch, tmp_path):
    fem = load_module()

    monkeypatch.setattr(shutil, "which", lambda name: None)
    skipped = fem.run_calculix_if_available(tmp_path / "job.inp", tmp_path)
    assert skipped["status"] == "skipped"
    assert skipped["reason"] == "ccx not found"

    decks = {"thermal": tmp_path / "thermal.inp", "thermomechanical": tmp_path / "mech.inp"}
    for path in decks.values():
        path.write_text("*HEADING\n", encoding="utf-8")
    all_skipped = fem.run_calculix_decks(decks, tmp_path, no_solver=True)
    assert all_skipped["status"] == "skipped"
    assert set(all_skipped["decks"]) == {"thermal", "thermomechanical"}
    assert all(deck["reason"] == "no_solver_requested" for deck in all_skipped["decks"].values())

    with pytest.raises(RuntimeError):
        fem.run_calculix_if_available(tmp_path / "job.inp", tmp_path, require_solver_smoke=True)

    with pytest.raises(ValueError):
        fem.run_calculix_if_available(
            tmp_path / "job.inp",
            tmp_path,
            require_solver_smoke=True,
            no_solver=True,
        )

    bad = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--output",
            str(tmp_path / "o"),
            "--report",
            str(tmp_path / "r.md"),
            "--no-solver",
            "--require-solver-smoke",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert bad.returncode != 0
    assert "not allowed with argument" in bad.stderr or "mutually" in bad.stderr


def test_solver_wrapper_records_failure_without_crashing_report(monkeypatch, tmp_path):
    fem = load_module()

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ccx")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=2,
            stdout="CalculiX Version 2.21\nout",
            stderr="err",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    status = fem.run_calculix_if_available(tmp_path / "job.inp", tmp_path)
    assert status["status"] == "failed"
    assert status["returncode"] == 2
    assert status["version"] == "CalculiX Version 2.21"
    assert "out" in status["stdout"]
    assert "err" in status["stderr"]

    with pytest.raises(RuntimeError):
        fem.run_calculix_if_available(tmp_path / "job.inp", tmp_path, require_solver_smoke=True)
