#!/usr/bin/env python3
"""Generate interactive Plotly comparison plots between OrcaWave extracted
RAO data and benchmark reference data.

Reads:
  - Extracted xlsx: digitalmodel/tests/fixtures/solver/test01_unit_box.xlsx
  - Benchmark YAML: digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.1/benchmark/hydro_data.yml

Outputs:
  - docs/reports/rao-comparison-test01-unit-box.html (self-contained)

Usage (from workspace-hub root):
    PYTHONPATH=digitalmodel/src uv run python scripts/solver/generate_rao_comparison_plots.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import yaml
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Paths (relative to workspace-hub root)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent
XLSX_PATH = ROOT / "digitalmodel/tests/fixtures/solver/test01_unit_box.xlsx"
BENCHMARK_PATH = (
    ROOT
    / "digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.1/benchmark/hydro_data.yml"
)
OUTPUT_HTML = ROOT / "docs/reports/rao-comparison-test01-unit-box.html"

DOF_NAMES = ["surge", "sway", "heave", "roll", "pitch", "yaw"]
DOF_LABELS = ["Surge", "Sway", "Heave", "Roll", "Pitch", "Yaw"]
DOF_UNITS = ["m/m", "m/m", "m/m", "deg/m", "deg/m", "deg/m"]

# OrcFxAPI returns rotational RAOs in radians/m.
# Benchmark YAML stores them in degrees/m.
# Indices 3,4,5 (Roll, Pitch, Yaw) need rad→deg conversion from extracted xlsx.
ROTATIONAL_DOFS = {3, 4, 5}
RAD_TO_DEG = 180.0 / np.pi

# Plotly color palette for headings
COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
]


def load_extracted_rao():
    """Load RAO data from xlsx using rao_extractor module."""
    from digitalmodel.hydrodynamics.hull_library.rao_extractor import xlsx_to_rao_data

    rao = xlsx_to_rao_data(XLSX_PATH)
    return rao


def load_benchmark():
    """Load benchmark reference data from hydro_data.yml.

    Returns
    -------
    dict with keys:
        frequencies : np.ndarray (n_freq,)
        headings    : np.ndarray (n_heading,)
        solvers     : dict[solver_name] -> dict[dof_name] -> np.ndarray (n_freq, n_heading)
    """
    with open(BENCHMARK_PATH) as f:
        data = yaml.safe_load(f)

    grid = data["grid"]
    frequencies = np.array(grid["frequencies_rad_s"], dtype=np.float64)
    headings = np.array(grid["headings_deg"], dtype=np.float64)

    solvers = {}
    for solver_name, solver_data in data.get("solvers", {}).items():
        raos = solver_data.get("raos", {})
        dof_amplitudes = {}
        for dof in DOF_NAMES:
            if dof in raos:
                mag = raos[dof].get("magnitude", [])
                dof_amplitudes[dof] = np.array(mag, dtype=np.float64)
        solvers[solver_name] = dof_amplitudes

    return {
        "frequencies": frequencies,
        "headings": headings,
        "solvers": solvers,
    }


def compute_max_relative_diff(
    freq_ext: np.ndarray,
    amp_ext: np.ndarray,
    freq_bench: np.ndarray,
    amp_bench: np.ndarray,
    abs_tol: float = 1e-6,
) -> tuple[float, float]:
    """Compute max relative difference between extracted and benchmark.

    Interpolates extracted data onto benchmark frequency grid, then computes:
        max(|ext - bench| / max(|bench|, eps))

    Near-zero amplitudes (max < abs_tol) are flagged but not penalized.

    Returns
    -------
    (max_rel_diff, max_abs_diff)
        NaN if no valid comparison points.
    """
    eps = 1e-12

    # Find overlapping frequency range
    f_min = max(freq_ext[0], freq_bench[0])
    f_max = min(freq_ext[-1], freq_bench[-1])
    if f_min >= f_max:
        return float("nan"), float("nan")

    # Mask benchmark frequencies within range
    mask = (freq_bench >= f_min) & (freq_bench <= f_max)
    if not np.any(mask):
        return float("nan"), float("nan")

    bench_f = freq_bench[mask]
    bench_a = amp_bench[mask]

    # Interpolate extracted onto benchmark grid
    ext_interp = np.interp(bench_f, freq_ext, amp_ext)

    abs_diff = np.abs(ext_interp - bench_a)
    max_abs = float(np.nanmax(abs_diff))

    # If both signals are near zero, relative diff is meaningless
    peak = max(np.max(np.abs(bench_a)), np.max(np.abs(ext_interp)))
    if peak < abs_tol:
        return 0.0, max_abs

    denom = np.maximum(np.abs(bench_a), eps)
    rel_diff = abs_diff / denom

    # Only consider points where benchmark is above noise floor
    significant = np.abs(bench_a) > abs_tol
    if not np.any(significant):
        return 0.0, max_abs

    return float(np.nanmax(rel_diff[significant])), max_abs


def build_comparison_figure(extracted_rao, benchmark):
    """Build 2x3 Plotly figure comparing extracted vs benchmark RAOs."""
    fig = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=[
            f"{label} ({unit})" for label, unit in zip(DOF_LABELS, DOF_UNITS)
        ],
        horizontal_spacing=0.06,
        vertical_spacing=0.12,
    )

    # Extracted data
    ext_freq = extracted_rao.frequencies
    ext_dirs = extracted_rao.directions
    ext_amps = extracted_rao.amplitudes  # (n_freq, n_dir, 6)

    # Benchmark data
    bench_freq = benchmark["frequencies"]
    bench_headings = benchmark["headings"]
    bench_solvers = benchmark["solvers"]

    # Track max relative differences
    max_rel_diffs = {}

    # --- Plot extracted data (solid lines) ---
    for dir_idx, heading in enumerate(ext_dirs):
        color = COLORS[dir_idx % len(COLORS)]
        for dof_idx, dof_name in enumerate(DOF_NAMES):
            row = dof_idx // 3 + 1
            col = dof_idx % 3 + 1

            amp = ext_amps[:, dir_idx, dof_idx].copy()
            # Convert rotational DOFs from rad/m to deg/m
            if dof_idx in ROTATIONAL_DOFS:
                amp = amp * RAD_TO_DEG

            fig.add_trace(
                go.Scatter(
                    x=ext_freq,
                    y=amp,
                    mode="lines",
                    name=f"Extracted / {heading}°",
                    line=dict(color=color, width=2),
                    legendgroup=f"ext_{heading}",
                    showlegend=(dof_idx == 0),
                    hovertemplate=(
                        f"Extracted<br>Heading: {heading}°<br>"
                        "Freq: %{x:.2f} rad/s<br>Amp: %{y:.4f}<extra></extra>"
                    ),
                ),
                row=row,
                col=col,
            )

    # --- Plot benchmark data (dashed lines) ---
    for solver_name, dof_amplitudes in bench_solvers.items():
        for hdg_idx, heading in enumerate(bench_headings):
            color = COLORS[hdg_idx % len(COLORS)]
            # Use different dash per solver
            solver_idx = list(bench_solvers.keys()).index(solver_name)
            dash_styles = ["dash", "dot", "dashdot"]
            dash = dash_styles[solver_idx % len(dash_styles)]

            for dof_idx, dof_name in enumerate(DOF_NAMES):
                row = dof_idx // 3 + 1
                col = dof_idx % 3 + 1

                if dof_name not in dof_amplitudes:
                    continue

                amp_2d = dof_amplitudes[dof_name]  # (n_freq, n_heading)
                if hdg_idx >= amp_2d.shape[1]:
                    continue
                amp = amp_2d[:, hdg_idx]

                short_solver = solver_name.replace("OrcaWave ", "OW")
                legend_label = f"{short_solver} / {heading}°"

                fig.add_trace(
                    go.Scatter(
                        x=bench_freq,
                        y=amp,
                        mode="lines",
                        name=legend_label,
                        line=dict(color=color, width=2, dash=dash),
                        legendgroup=f"bench_{solver_name}_{heading}",
                        showlegend=(dof_idx == 0),
                        hovertemplate=(
                            f"{solver_name}<br>Heading: {heading}°<br>"
                            "Freq: %{x:.2f} rad/s<br>Amp: %{y:.4f}<extra></extra>"
                        ),
                    ),
                    row=row,
                    col=col,
                )

                # Compute relative differences (match heading)
                matching_dir_idx = None
                for ei, ed in enumerate(ext_dirs):
                    if abs(ed - heading) < 0.5:
                        matching_dir_idx = ei
                        break

                if matching_dir_idx is not None:
                    ext_amp_1d = ext_amps[:, matching_dir_idx, dof_idx].copy()
                    if dof_idx in ROTATIONAL_DOFS:
                        ext_amp_1d = ext_amp_1d * RAD_TO_DEG
                    key = (dof_name, solver_name, heading)
                    rel_diff, abs_diff = compute_max_relative_diff(
                        ext_freq, ext_amp_1d, bench_freq, amp
                    )
                    max_rel_diffs[key] = (rel_diff, abs_diff)

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text="OrcaWave RAO Validation — Test01 Unit Box (L00 Case 2.1)",
            font=dict(size=18),
            x=0.5,
        ),
        height=700,
        width=1400,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
        margin=dict(t=80, b=120, l=60, r=30),
    )

    for dof_idx in range(6):
        row = dof_idx // 3 + 1
        col = dof_idx % 3 + 1
        axis_suffix = "" if (row == 1 and col == 1) else str((row - 1) * 3 + col)
        fig.update_xaxes(
            title_text="Frequency (rad/s)" if row == 2 else "",
            row=row,
            col=col,
        )
        fig.update_yaxes(
            title_text="Amplitude" if col == 1 else "",
            row=row,
            col=col,
        )

    return fig, max_rel_diffs


def format_summary(max_rel_diffs: dict) -> str:
    """Format a text summary of max relative differences per DOF.

    max_rel_diffs values are (rel_diff, abs_diff) tuples.
    """
    lines = [
        "=" * 70,
        "RAO Comparison Summary — Max Relative Differences",
        "  (near-zero amplitudes excluded from relative comparison)",
        "=" * 70,
        "",
    ]

    # Group by DOF
    for dof_name, dof_label in zip(DOF_NAMES, DOF_LABELS):
        dof_entries = {
            k: v for k, v in max_rel_diffs.items() if k[0] == dof_name
        }
        if not dof_entries:
            continue

        lines.append(f"  {dof_label}:")
        for (_, solver, heading), (rel_diff, abs_diff) in sorted(dof_entries.items()):
            if np.isnan(rel_diff):
                lines.append(f"    {solver} @ {heading}°:  N/A (no overlap)")
            else:
                pct = rel_diff * 100
                marker = " ✓" if pct < 1.0 else " ⚠" if pct < 5.0 else " ✗"
                lines.append(
                    f"    {solver} @ {heading:5.1f}°:  "
                    f"rel={pct:8.4f}%  abs={abs_diff:.2e}{marker}"
                )
        lines.append("")

    # Overall (only significant comparisons)
    valid_rel = [v[0] for v in max_rel_diffs.values() if not np.isnan(v[0])]
    if valid_rel:
        overall_max = max(valid_rel) * 100
        lines.append(f"  Overall max relative difference: {overall_max:.4f}%")
        if overall_max < 1.0:
            lines.append("  Status: PASS (< 1%)")
        elif overall_max < 5.0:
            lines.append("  Status: WARNING (< 5%)")
        else:
            lines.append("  Status: REVIEW (>= 5% — check if near-zero DOFs)")
    else:
        lines.append("  No valid comparisons found.")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    print("Loading extracted RAO data from xlsx...")
    extracted_rao = load_extracted_rao()
    print(
        f"  Vessel: {extracted_rao.vessel_name}, "
        f"Frequencies: {len(extracted_rao.frequencies)}, "
        f"Directions: {list(extracted_rao.directions)}"
    )

    print("Loading benchmark reference data from hydro_data.yml...")
    benchmark = load_benchmark()
    print(
        f"  Frequencies: {len(benchmark['frequencies'])}, "
        f"Headings: {list(benchmark['headings'])}, "
        f"Solvers: {list(benchmark['solvers'].keys())}"
    )

    print("Building comparison figure...")
    fig, max_rel_diffs = build_comparison_figure(extracted_rao, benchmark)

    # Summary
    summary = format_summary(max_rel_diffs)
    print()
    print(summary)

    # Save HTML
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_HTML), include_plotlyjs=True)
    print(f"\nHTML report saved to: {OUTPUT_HTML}")
    print(f"  Size: {OUTPUT_HTML.stat().st_size / 1024:.0f} KB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
