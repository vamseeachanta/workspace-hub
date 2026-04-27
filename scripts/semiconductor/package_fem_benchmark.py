#!/usr/bin/env python3
"""Semiconductor package thermal / thermo-mechanical FEM benchmark.

This script creates a small, portfolio-safe educational benchmark for a
multilayer semiconductor package.  It intentionally avoids proprietary package
or standards data and uses SI units throughout.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PackageLayer:
    name: str
    thickness_m: float
    material_id: str
    mesh_divisions_z: int

    def __post_init__(self) -> None:
        if self.thickness_m <= 0:
            raise ValueError(f"layer {self.name} thickness must be positive")
        if self.mesh_divisions_z <= 0:
            raise ValueError(f"layer {self.name} mesh divisions must be positive")


@dataclass(frozen=True)
class Material:
    name: str
    E_Pa: float
    nu: float
    cte_per_K: float
    k_W_m_K: float
    source: str
    source_note: str

    def __post_init__(self) -> None:
        if self.E_Pa <= 0 or not (0 <= self.nu < 0.5):
            raise ValueError(f"invalid elastic constants for {self.name}")
        if self.cte_per_K <= 0 or self.k_W_m_K <= 0:
            raise ValueError(f"invalid thermal constants for {self.name}")
        if not self.source.strip() or not self.source_note.strip():
            raise ValueError(f"missing material provenance for {self.name}")


@dataclass(frozen=True)
class BenchmarkSpec:
    length_m: float
    width_m: float
    layers: tuple[PackageLayer, ...]
    materials: dict[str, Material]
    nx: int
    ny: int
    ambient_C: float
    junction_C: float
    power_W: float
    units: str = "SI"

    @property
    def total_thickness_m(self) -> float:
        return sum(layer.thickness_m for layer in self.layers)

    @property
    def area_m2(self) -> float:
        return self.length_m * self.width_m

    def layer_offsets(self) -> list[tuple[PackageLayer, float, float]]:
        out: list[tuple[PackageLayer, float, float]] = []
        z = 0.0
        for layer in self.layers:
            z_next = z + layer.thickness_m
            out.append((layer, z, z_next))
            z = z_next
        return out

    def validate(self) -> None:
        if self.units != "SI":
            raise ValueError("benchmark uses SI units only")
        if self.length_m <= 0 or self.width_m <= 0:
            raise ValueError("package dimensions must be positive")
        if self.nx <= 0 or self.ny <= 0:
            raise ValueError("mesh nx/ny must be positive")
        for layer in self.layers:
            if layer.material_id not in self.materials:
                raise ValueError(f"missing material {layer.material_id}")


@dataclass(frozen=True)
class Node:
    id: int
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Element:
    id: int
    node_ids: tuple[int, int, int, int, int, int, int, int]
    material_id: str
    layer_name: str


@dataclass(frozen=True)
class MeshModel:
    nodes: list[Node]
    elements: list[Element]
    sets: dict[str, list[int]]


def build_default_spec(nx: int = 4, ny: int = 4) -> BenchmarkSpec:
    """Return a small educational package stack-up using SI units."""
    materials = {
        "fr4": Material(
            name="FR-4 substrate (representative)",
            E_Pa=22.0e9,
            nu=0.28,
            cte_per_K=16.0e-6,
            k_W_m_K=0.30,
            source="Representative open engineering handbook value",
            source_note="Educational FR-4 approximation; not a vendor datasheet or IPC requirement.",
        ),
        "silicon": Material(
            name="Silicon die (representative)",
            E_Pa=130.0e9,
            nu=0.28,
            cte_per_K=2.6e-6,
            k_W_m_K=130.0,
            source="Representative open engineering handbook value",
            source_note="Educational silicon approximation for portfolio benchmark only.",
        ),
        "mold": Material(
            name="Epoxy mold compound (representative)",
            E_Pa=18.0e9,
            nu=0.35,
            cte_per_K=12.0e-6,
            k_W_m_K=0.70,
            source="Representative open engineering handbook value",
            source_note="Educational mold-compound approximation; not proprietary package data.",
        ),
        "solder": Material(
            name="Solder zone (lumped representative)",
            E_Pa=35.0e9,
            nu=0.36,
            cte_per_K=22.0e-6,
            k_W_m_K=50.0,
            source="Representative open engineering handbook value",
            source_note="Lumped interconnect/support layer for benchmark simplification.",
        ),
    }
    layers = (
        PackageLayer("solder_zone", 0.00012, "solder", 1),
        PackageLayer("substrate", 0.00080, "fr4", 2),
        PackageLayer("die", 0.00025, "silicon", 1),
        PackageLayer("mold", 0.00065, "mold", 2),
    )
    spec = BenchmarkSpec(
        length_m=0.010,
        width_m=0.010,
        layers=layers,
        materials=materials,
        nx=nx,
        ny=ny,
        ambient_C=25.0,
        junction_C=85.0,
        power_W=2.0,
    )
    spec.validate()
    return spec


def _z_levels(spec: BenchmarkSpec) -> tuple[list[float], list[str], list[str]]:
    z_values = [0.0]
    layer_for_interval: list[str] = []
    material_for_interval: list[str] = []
    z = 0.0
    for layer in spec.layers:
        dz = layer.thickness_m / layer.mesh_divisions_z
        for _ in range(layer.mesh_divisions_z):
            layer_for_interval.append(layer.name)
            material_for_interval.append(layer.material_id)
            z += dz
            z_values.append(z)
    return z_values, layer_for_interval, material_for_interval


def structured_hex_mesh(spec: BenchmarkSpec) -> MeshModel:
    spec.validate()
    z_values, layer_for_interval, material_for_interval = _z_levels(spec)
    nodes: list[Node] = []
    node_index: dict[tuple[int, int, int], int] = {}
    nid = 1
    for k, z in enumerate(z_values):
        for j in range(spec.ny + 1):
            y = spec.width_m * j / spec.ny
            for i in range(spec.nx + 1):
                x = spec.length_m * i / spec.nx
                node_index[(i, j, k)] = nid
                nodes.append(Node(nid, x, y, z))
                nid += 1

    elements: list[Element] = []
    eid = 1
    for k in range(len(z_values) - 1):
        for j in range(spec.ny):
            for i in range(spec.nx):
                n = node_index
                node_ids = (
                    n[(i, j, k)],
                    n[(i + 1, j, k)],
                    n[(i + 1, j + 1, k)],
                    n[(i, j + 1, k)],
                    n[(i, j, k + 1)],
                    n[(i + 1, j, k + 1)],
                    n[(i + 1, j + 1, k + 1)],
                    n[(i, j + 1, k + 1)],
                )
                elements.append(
                    Element(eid, node_ids, material_for_interval[k], layer_for_interval[k])
                )
                eid += 1

    bottom = [node.id for node in nodes if math.isclose(node.z, 0.0, abs_tol=1e-12)]
    top_z = spec.total_thickness_m
    top = [node.id for node in nodes if math.isclose(node.z, top_z, rel_tol=0, abs_tol=1e-12)]
    sets: dict[str, list[int]] = {"bottom": bottom, "top": top}
    for layer in spec.layers:
        sets[layer.name] = [element.id for element in elements if element.layer_name == layer.name]
    return MeshModel(nodes=nodes, elements=elements, sets=sets)


def _fmt(value: float) -> str:
    return f"{value:.9g}"


def node_temperature_map(spec: BenchmarkSpec, mesh: MeshModel) -> dict[int, float]:
    """Return a power-based 1D thermal-resistance temperature profile by node id."""
    cumulative_points: list[tuple[float, float, float, float]] = []
    temperature = spec.ambient_C
    z0 = 0.0
    for layer in spec.layers:
        material = spec.materials[layer.material_id]
        layer_delta = spec.power_W * layer.thickness_m / (material.k_W_m_K * spec.area_m2)
        z1 = z0 + layer.thickness_m
        t0 = temperature
        t1 = temperature + layer_delta
        cumulative_points.append((z0, z1, t0, t1))
        temperature = t1
        z0 = z1
    temps: dict[int, float] = {}
    for node in mesh.nodes:
        for z_start, z_end, t_start, t_end in cumulative_points:
            if z_start - 1e-12 <= node.z <= z_end + 1e-12:
                frac = 0.0 if math.isclose(z_end, z_start) else (node.z - z_start) / (z_end - z_start)
                temps[node.id] = t_start + frac * (t_end - t_start)
                break
        else:
            raise ValueError(f"node {node.id} at z={node.z} not inside package thickness")
    return temps


def write_calculix_inputs(spec: BenchmarkSpec, mesh: MeshModel, output_dir: str | Path) -> dict[str, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    def common_sections(element_type: str) -> list[str]:
        lines = [
            "** Semiconductor package FEM benchmark — SI units (m, N, Pa, W, K)",
            "** Portfolio benchmark only; material values are representative educational assumptions.",
            "*NODE",
        ]
        for node in mesh.nodes:
            lines.append(f"{node.id}, {_fmt(node.x)}, {_fmt(node.y)}, {_fmt(node.z)}")
        lines.append(f"*ELEMENT, TYPE={element_type}, ELSET=ALL_ELEMENTS")
        for element in mesh.elements:
            lines.append(f"{element.id}, " + ", ".join(str(n) for n in element.node_ids))
        for layer in spec.layers:
            ids = [str(e.id) for e in mesh.elements if e.layer_name == layer.name]
            lines.append(f"*ELSET, ELSET={layer.name.upper()}")
            lines.extend(_chunks(ids))
        for material_id, material in spec.materials.items():
            lines.extend(
                [
                    f"** Material provenance: {material.source} — {material.source_note}",
                    f"*MATERIAL, NAME={material_id.upper()}",
                    "*ELASTIC",
                    f"{_fmt(material.E_Pa)}, {_fmt(material.nu)}",
                    "*EXPANSION",
                    f"{_fmt(material.cte_per_K)}",
                    "*CONDUCTIVITY",
                    f"{_fmt(material.k_W_m_K)}",
                ]
            )
        for layer in spec.layers:
            lines.append(f"*SOLID SECTION, ELSET={layer.name.upper()}, MATERIAL={layer.material_id.upper()}")
            lines.append("")
        all_node_ids = [str(node.id) for node in mesh.nodes]
        bottom_ids = [str(n) for n in mesh.sets["bottom"]]
        top_ids = [str(n) for n in mesh.sets["top"]]
        lines.append("*NSET, NSET=ALLNODES")
        lines.extend(_chunks(all_node_ids))
        lines.append("*NSET, NSET=BOTTOM")
        lines.extend(_chunks(bottom_ids))
        lines.append("*NSET, NSET=TOP")
        lines.extend(_chunks(top_ids))
        return lines

    thermal = common_sections("DC3D8")
    thermal.extend(
        [
            "*INITIAL CONDITIONS, TYPE=TEMPERATURE",
            f"ALLNODES, {spec.ambient_C:.3f}",
            "*STEP",
            "*HEAT TRANSFER, STEADY STATE",
            "*BOUNDARY",
            f"BOTTOM, 11, 11, {spec.ambient_C:.3f}",
            "** Applied volumetric heat source derived from power_W=2 over the die volume.",
            "*DFLUX",
            f"DIE, BF, {_fmt(spec.power_W / (spec.area_m2 * next(layer.thickness_m for layer in spec.layers if layer.name == 'die')))}",
            "*NODE FILE",
            "NT",
            "*EL FILE",
            "HFL",
            "*NODE PRINT, NSET=TOP",
            "NT",
            "*END STEP",
        ]
    )
    thermal_path = out / "package_thermal.inp"
    thermal_path.write_text("\n".join(thermal) + "\n", encoding="utf-8")

    mech = common_sections("C3D8")
    temperature_lines = [
        "** Thermo-mechanical temperatures use the same power-based 1D thermal-resistance profile as the analytical summary.",
        "*TEMPERATURE",
    ]
    profile_temperatures = node_temperature_map(spec, mesh)
    for node in mesh.nodes:
        temperature_lines.append(f"{node.id}, {profile_temperatures[node.id]:.6f}")
    mech.extend(
        [
            "*INITIAL CONDITIONS, TYPE=TEMPERATURE",
            f"ALLNODES, {spec.ambient_C:.3f}",
            "*STEP",
            "*STATIC",
        ]
    )
    mech.extend(temperature_lines)
    mech.extend(
        [
            "*BOUNDARY",
            "BOTTOM, 1, 3, 0.0",
            "*CLOAD",
            "*NODE FILE",
            "U",
            "*EL FILE",
            "S",
            "*NODE PRINT, NSET=TOP",
            "U",
            "*EL PRINT, ELSET=ALL_ELEMENTS",
            "S",
            "*END STEP",
        ]
    )
    mech_path = out / "package_thermomechanical.inp"
    mech_path.write_text("\n".join(mech) + "\n", encoding="utf-8")
    return {"thermal": thermal_path, "thermomechanical": mech_path}


def _chunks(values: Iterable[str], width: int = 12) -> list[str]:
    vals = list(values)
    return [", ".join(vals[i : i + width]) for i in range(0, len(vals), width)] or [""]


def _parse_calculix_version(stdout: str, stderr: str = "") -> str | None:
    for line in (stdout + "\n" + stderr).splitlines():
        stripped = line.strip()
        if stripped.startswith("CalculiX Version"):
            return stripped
    return None


def run_calculix_if_available(
    input_path: str | Path,
    output_dir: str | Path,
    require_solver_smoke: bool = False,
    no_solver: bool = False,
) -> dict[str, object]:
    if no_solver and require_solver_smoke:
        raise ValueError("--no-solver and --require-solver-smoke are mutually exclusive")
    if no_solver:
        return {"status": "skipped", "reason": "no_solver_requested"}
    ccx = shutil.which("ccx")
    if not ccx:
        if require_solver_smoke:
            raise RuntimeError("ccx not found but solver smoke was required")
        return {"status": "skipped", "reason": "ccx not found"}

    path = Path(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    job = path.with_suffix("").name
    try:
        completed = subprocess.run(
            [ccx, job],
            cwd=path.parent,
            text=True,
            capture_output=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        status = {
            "status": "failed",
            "reason": "timeout",
            "command": f"{ccx} {job}",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }
        if require_solver_smoke:
            raise RuntimeError("CalculiX smoke timed out")
        return status

    artifacts = []
    for suffix in (".frd", ".dat", ".cvg", ".sta"):
        artifact = path.with_suffix(suffix)
        if artifact.exists() and artifact.stat().st_size > 0:
            artifacts.append(artifact.name)
    result = {
        "status": "ran" if completed.returncode == 0 and any(a.endswith((".frd", ".dat")) for a in artifacts) else "failed",
        "returncode": completed.returncode,
        "command": f"{ccx} {job}",
        "version": _parse_calculix_version(completed.stdout, completed.stderr),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "artifacts": artifacts,
    }
    if result["status"] == "failed" and require_solver_smoke:
        raise RuntimeError(f"CalculiX smoke failed for {path.name}: rc={completed.returncode}")
    return result


def run_calculix_decks(
    deck_paths: dict[str, Path],
    output_dir: str | Path,
    require_solver_smoke: bool = False,
    no_solver: bool = False,
) -> dict[str, object]:
    """Run or skip every generated CalculiX deck and aggregate deck status."""
    if no_solver and require_solver_smoke:
        raise ValueError("--no-solver and --require-solver-smoke are mutually exclusive")
    decks: dict[str, dict[str, object]] = {}
    for name, path in deck_paths.items():
        decks[name] = run_calculix_if_available(
            path,
            output_dir,
            require_solver_smoke=require_solver_smoke,
            no_solver=no_solver,
        )
    statuses = {str(deck.get("status")) for deck in decks.values()}
    if statuses == {"skipped"}:
        status = "skipped"
        reasons = sorted({str(deck.get("reason", "")) for deck in decks.values()})
        reason = reasons[0] if len(reasons) == 1 else "; ".join(reasons)
    elif statuses == {"ran"}:
        status = "ran"
        reason = "all_decks_solver_smoke_ran"
    elif "failed" in statuses:
        status = "failed"
        reason = "one_or_more_decks_failed"
    else:
        status = "partial"
        reason = "mixed_solver_status"
    versions = sorted({str(deck.get("version")) for deck in decks.values() if deck.get("version")})
    return {"status": status, "reason": reason, "versions": versions, "decks": decks}


def _layer_summary(spec: BenchmarkSpec, mesh: MeshModel) -> list[dict[str, object]]:
    rows = []
    for layer, z0, z1 in spec.layer_offsets():
        mat = spec.materials[layer.material_id]
        element_count = sum(1 for e in mesh.elements if e.layer_name == layer.name)
        rows.append(
            {
                "layer": layer.name,
                "material_id": layer.material_id,
                "z_min_m": z0,
                "z_max_m": z1,
                "thickness_m": layer.thickness_m,
                "elements": element_count,
                "k_W_m_K": mat.k_W_m_K,
                "cte_per_K": mat.cte_per_K,
                "E_Pa": mat.E_Pa,
            }
        )
    return rows


def summarize_benchmark(spec: BenchmarkSpec, mesh: MeshModel, solver_status: dict[str, object]) -> dict[str, object]:
    area = spec.area_m2
    layer_rows = _layer_summary(spec, mesh)
    resistances = [row["thickness_m"] / (row["k_W_m_K"] * area) for row in layer_rows]
    total_r = float(sum(resistances))
    delta_t = spec.power_W * total_r
    substrate_cte = spec.materials["fr4"].cte_per_K
    strains = [abs(spec.materials[row["material_id"]].cte_per_K - substrate_cte) * delta_t for row in layer_rows]
    max_strain = float(max(strains))
    warpage_um = max_strain * spec.length_m * 1.0e6 / 2.0
    aspect = max(spec.length_m / spec.nx, spec.width_m / spec.ny) / min(
        layer.thickness_m / layer.mesh_divisions_z for layer in spec.layers
    )
    return {
        "schema_version": "1.0.0",
        "benchmark": "semiconductor_package_fem",
        "units": "SI",
        "geometry": {
            "length_m": spec.length_m,
            "width_m": spec.width_m,
            "total_thickness_m": spec.total_thickness_m,
            "area_m2": area,
        },
        "loads": {
            "ambient_C": spec.ambient_C,
            "junction_C": spec.junction_C,
            "power_W": spec.power_W,
        },
        "mesh": {
            "node_count": len(mesh.nodes),
            "element_count": len(mesh.elements),
            "nx": spec.nx,
            "ny": spec.ny,
            "z_divisions": sum(layer.mesh_divisions_z for layer in spec.layers),
            "aspect_ratio_proxy": aspect,
        },
        "layers": layer_rows,
        "materials": {
            key: {
                "name": mat.name,
                "E_Pa": mat.E_Pa,
                "nu": mat.nu,
                "cte_per_K": mat.cte_per_K,
                "k_W_m_K": mat.k_W_m_K,
                "source": mat.source,
                "source_note": mat.source_note,
            }
            for key, mat in spec.materials.items()
        },
        "sanity_checks": {
            "thermal_resistance_K_per_W": total_r,
            "delta_T_K": delta_t,
            "max_free_strain": max_strain,
            "warpage_style_um": warpage_um,
            "formula_notes": [
                "R_layer = thickness / (k * area)",
                "delta_T = power_W * sum(R_layer)",
                "free_strain = abs(CTE_layer - CTE_substrate) * delta_T",
                "warpage_style_um = max_free_strain * length_m * 1e6 / 2",
            ],
        },
        "solver_status": solver_status,
        "limitations": [
            "Educational portfolio benchmark only; not production-certified.",
            "Not JEDEC-compliant, not IPC-compliant, not validated to JEDEC, and not for production signoff.",
            "Material constants are representative public/handbook-style approximations, not proprietary package data.",
        ],
        "artifact_hashes": {},
    }


def write_mesh_summary(spec: BenchmarkSpec, mesh: MeshModel, output_dir: str | Path) -> Path:
    path = Path(output_dir) / "mesh_summary.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["layer", "material_id", "z_min_m", "z_max_m", "thickness_m", "elements", "k_W_m_K", "cte_per_K", "E_Pa"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(_layer_summary(spec, mesh))
    return path


def write_result_profiles(spec: BenchmarkSpec, summary: dict[str, object], output_dir: str | Path) -> Path:
    path = Path(output_dir) / "result_profiles.csv"
    delta_t = float(summary["sanity_checks"]["delta_T_K"])
    rows = []
    total = spec.total_thickness_m
    z_midpoints = []
    for layer, z0, z1 in spec.layer_offsets():
        z = 0.5 * (z0 + z1)
        mat = spec.materials[layer.material_id]
        temperature = spec.ambient_C + delta_t * (z / total)
        normalized_stress = abs(mat.cte_per_K - spec.materials["fr4"].cte_per_K) / max(m.cte_per_K for m in spec.materials.values())
        warpage = float(summary["sanity_checks"]["warpage_style_um"]) * (z / total)
        rows.append(
            {
                "layer": layer.name,
                "z_m": f"{z:.9g}",
                "temperature_C": f"{temperature:.6g}",
                "normalized_stress": f"{normalized_stress:.6g}",
                "warpage_style_um": f"{warpage:.6g}",
            }
        )
        z_midpoints.append(z)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["layer", "z_m", "temperature_C", "normalized_stress", "warpage_style_um"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def _svg_header(width: int = 720, height: int = 360) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'


def write_stackup_svg(spec: BenchmarkSpec, output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "package_stackup.svg"
    x, y, w, h = 90, 50, 540, 240
    colors = ["#a5d8ff", "#ffd43b", "#d0bfff", "#ff8787", "#8ce99a"]
    lines = [_svg_header(), '<rect width="720" height="360" fill="#ffffff"/>']
    z = y + h
    for idx, layer in enumerate(spec.layers):
        lh = h * layer.thickness_m / spec.total_thickness_m
        z -= lh
        color = colors[idx % len(colors)]
        lines.append(f'<rect x="{x}" y="{z:.3f}" width="{w}" height="{lh:.3f}" fill="{color}" stroke="#222"/>')
        lines.append(f'<text x="{x + 12}" y="{z + lh / 2 + 4:.3f}" font-size="16" font-family="Arial">{layer.name}</text>')
    lines.append('<text x="90" y="330" font-size="14" font-family="Arial">Simplified package stackup (SI dimensions, educational assumptions)</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _read_profile_rows(output_dir: str | Path) -> list[dict[str, str]]:
    with (Path(output_dir) / "result_profiles.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_temperature_svg(output_dir: str | Path) -> Path:
    path = Path(output_dir) / "temperature_profile.svg"
    rows = _read_profile_rows(output_dir)
    temps = [float(r["temperature_C"]) for r in rows]
    tmin, tmax = min(temps), max(temps)
    denom = max(tmax - tmin, 1e-9)
    points = []
    for i, temp in enumerate(temps):
        px = 80 + i * (560 / max(len(temps) - 1, 1))
        py = 280 - (temp - tmin) / denom * 200
        points.append(f"{px:.3f},{py:.3f}")
    lines = [
        _svg_header(),
        '<rect width="720" height="360" fill="#ffffff"/>',
        '<text x="80" y="30" font-size="18" font-family="Arial">Through-thickness temperature estimate</text>',
        '<line x1="80" y1="280" x2="640" y2="280" stroke="#222"/>',
        '<line x1="80" y1="80" x2="80" y2="280" stroke="#222"/>',
        f'<polyline fill="none" stroke="#e03131" stroke-width="3" points="{" ".join(points)}"/>',
        f'<text x="80" y="320" font-size="13" font-family="Arial">{tmin:.2f} C to {tmax:.2f} C; analytical sanity profile, not production validation</text>',
        "</svg>",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_stress_warpage_svg(output_dir: str | Path) -> Path:
    path = Path(output_dir) / "stress_warpage_estimates.svg"
    rows = _read_profile_rows(output_dir)
    max_stress = max(float(r["normalized_stress"]) for r in rows) or 1.0
    lines = [
        _svg_header(),
        '<rect width="720" height="360" fill="#ffffff"/>',
        '<text x="70" y="30" font-size="18" font-family="Arial">CTE mismatch stress / warpage-style estimates</text>',
    ]
    for i, row in enumerate(rows):
        bar = 420 * float(row["normalized_stress"]) / max_stress
        y = 70 + i * 55
        lines.append(f'<text x="70" y="{y + 18}" font-size="13" font-family="Arial">{row["layer"]}</text>')
        lines.append(f'<rect x="190" y="{y}" width="{bar:.3f}" height="28" fill="#4dabf7" stroke="#222"/>')
        lines.append(f'<text x="620" y="{y + 18}" font-size="12" font-family="Arial">warp {float(row["warpage_style_um"]):.3g} um</text>')
    lines.append('<text x="70" y="330" font-size="13" font-family="Arial">Normalized educational estimates from CTE mismatch; not for production signoff</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(
    output_dir: str | Path,
    report_path: str | Path | None = None,
    summary_hashes: dict[str, str] | None = None,
) -> dict[str, str]:
    out = Path(output_dir)
    names = [p.name for p in out.iterdir() if p.is_file() and p.name != "artifact_manifest.sha256"]
    manifest_hashes = {name: sha256_file(out / name) for name in names}
    if report_path and Path(report_path).exists():
        report_key = _relative_link(out, Path(report_path))
        manifest_hashes[report_key] = sha256_file(Path(report_path))
    manifest = out / "artifact_manifest.sha256"
    manifest.write_text("".join(f"{digest}  {name}\n" for name, digest in sorted(manifest_hashes.items())), encoding="utf-8")
    return summary_hashes if summary_hashes is not None else manifest_hashes


def write_summary(summary: dict[str, object], output_dir: str | Path) -> Path:
    path = Path(output_dir) / "benchmark_summary.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_readme(output_dir: str | Path) -> Path:
    path = Path(output_dir) / "README.md"
    path.write_text(
        "# Semiconductor package FEM benchmark artifacts\n\n"
        "Generated by `scripts/semiconductor/package_fem_benchmark.py`.\n\n"
        "Regenerate deterministic artifacts with:\n\n"
        "```bash\n"
        "uv run python scripts/semiconductor/package_fem_benchmark.py --output data/semiconductor/package_fem_benchmark --report docs/reports/semiconductor-package-fem-benchmark.md --no-solver\n"
        "```\n\n"
        "Use `--require-solver-smoke` in a temporary output directory when local CalculiX (`ccx`) is available.\n",
        encoding="utf-8",
    )
    return path


def _relative_link(from_dir: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def render_report(spec: BenchmarkSpec, summary: dict[str, object], output_dir: str | Path, report_path: str | Path) -> Path:
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    solver = summary["solver_status"]
    out = Path(output_dir)
    stackup_link = _relative_link(report.parent, out / "package_stackup.svg")
    temperature_link = _relative_link(report.parent, out / "temperature_profile.svg")
    stress_link = _relative_link(report.parent, out / "stress_warpage_estimates.svg")
    lines = [
        "# Semiconductor Package FEM Benchmark",
        "",
        "## Executive Summary",
        "This portfolio benchmark builds a simplified semiconductor package stackup, emits CalculiX input decks, and generates deterministic temperature/stress/warpage-style plots. It is not production-certified and is not for production signoff.",
        "",
        "## Boundary Conditions",
        "- Bottom package surface is the reference/support surface.",
        "- Top package surface represents the junction-side thermal boundary.",
        "- Thermo-mechanical deck uses simplified bottom constraints and thermal expansion material data.",
        "",
        "## Loads",
        f"- Ambient temperature: {spec.ambient_C:.1f} C",
        f"- Junction temperature: {spec.junction_C:.1f} C",
        f"- Representative package power: {spec.power_W:.3g} W",
        "",
        "## Materials and Provenance",
    ]
    for key, mat in spec.materials.items():
        lines.append(f"- `{key}`: E={mat.E_Pa:.3g} Pa, nu={mat.nu:.3g}, CTE={mat.cte_per_K:.3g} 1/K, k={mat.k_W_m_K:.3g} W/m/K. Source: {mat.source}; note: {mat.source_note}")
    lines.extend(
        [
            "",
            "## Mesh and Convergence Notes",
            f"- Nodes: {summary['mesh']['node_count']}",
            f"- Elements: {summary['mesh']['element_count']}",
            "- Structured mesh is intentionally small for CI transparency; a production package model would require formal mesh refinement.",
            "",
            "## Convergence and Smoke Checks",
            "| Check | Result |",
            "|---|---|",
            f"| Aspect-ratio proxy | {summary['mesh']['aspect_ratio_proxy']:.6g} |",
            f"| Analytical delta-T positive | {summary['sanity_checks']['delta_T_K']:.6g} K |",
            f"| Solver aggregate status | {solver.get('status')} |",
            f"| Solver versions | {', '.join(solver.get('versions', [])) if solver.get('versions') else 'not run in committed no-solver artifact'} |",
            "| Solver decks covered | " + ", ".join(sorted(solver.get('decks', {}).keys())) + " |",
            "",
            "## Solver Status",
            f"- Status: `{solver.get('status')}`",
            f"- Reason/command: `{solver.get('reason') or solver.get('command') or 'n/a'}`",
        ]
    )
    for deck_name, deck in sorted(solver.get("decks", {}).items()):
        lines.append(f"- `{deck_name}`: `{deck.get('status')}` — `{deck.get('reason') or deck.get('command') or 'n/a'}`")
    lines.extend(
        [
            "",
            "## Result Plots",
            "- Stackup schematic: `package_stackup.svg`",
            "- Temperature profile: `temperature_profile.svg`",
            "- Stress/warpage-style estimate: `stress_warpage_estimates.svg`",
            "- Source profile data: `result_profiles.csv`",
            "",
            f"![Package stackup]({stackup_link})",
            f"![Temperature profile]({temperature_link})",
            f"![Stress and warpage estimates]({stress_link})",
            "",
            "## Sanity Checks",
            f"- Thermal resistance: {summary['sanity_checks']['thermal_resistance_K_per_W']:.6g} K/W",
            f"- Delta-T estimate: {summary['sanity_checks']['delta_T_K']:.6g} K",
            f"- Max free strain: {summary['sanity_checks']['max_free_strain']:.6g}",
            f"- Warpage-style estimate: {summary['sanity_checks']['warpage_style_um']:.6g} um",
            "",
            "## Standards and Use Limitations",
            "This benchmark is not JEDEC-compliant, not IPC-compliant, not validated to JEDEC, not production-certified, and not for production signoff. It does not extract or claim proprietary JEDEC/IPC requirements; terminology is used only for portfolio-safe engineering communication.",
            "",
            "## Regeneration",
            "```bash",
            "uv run python scripts/semiconductor/package_fem_benchmark.py --output data/semiconductor/package_fem_benchmark --report docs/reports/semiconductor-package-fem-benchmark.md --no-solver",
            "```",
            "",
        ]
    )
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def generate(output_dir: str | Path, report_path: str | Path, no_solver: bool, require_solver_smoke: bool) -> dict[str, object]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    spec = build_default_spec()
    mesh = structured_hex_mesh(spec)
    write_readme(out)
    deck_paths = write_calculix_inputs(spec, mesh, out)
    solver_status = run_calculix_decks(
        deck_paths,
        out,
        require_solver_smoke=require_solver_smoke,
        no_solver=no_solver,
    )
    summary = summarize_benchmark(spec, mesh, solver_status)
    write_mesh_summary(spec, mesh, out)
    write_summary(summary, out)
    write_result_profiles(spec, summary, out)
    write_stackup_svg(spec, out)
    write_temperature_svg(out)
    write_stress_warpage_svg(out)
    render_report(spec, summary, out, report_path)
    summary_hashes = {
        p.name: sha256_file(p)
        for p in sorted(out.iterdir())
        if p.is_file() and p.name not in {"benchmark_summary.json", "artifact_manifest.sha256"}
    }
    if Path(report_path).exists():
        summary_hashes[_relative_link(out, Path(report_path))] = sha256_file(Path(report_path))
    summary["artifact_hashes"] = summary_hashes
    write_summary(summary, out)
    write_manifest(out, report_path, summary_hashes=summary_hashes)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Directory for generated benchmark artifacts")
    parser.add_argument("--report", required=True, help="Markdown report path")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--no-solver", action="store_true", help="Skip local CalculiX execution for deterministic regeneration")
    group.add_argument("--require-solver-smoke", action="store_true", help="Require local CalculiX smoke execution to succeed")
    return parser


def main(argv: list[str] | None = None) -> dict[str, object]:
    args = build_parser().parse_args(argv)
    summary = generate(args.output, args.report, no_solver=args.no_solver, require_solver_smoke=args.require_solver_smoke)
    print(f"wrote semiconductor package FEM benchmark to {args.output}")
    print(f"wrote report to {args.report}")
    return summary


if __name__ == "__main__":
    main()
