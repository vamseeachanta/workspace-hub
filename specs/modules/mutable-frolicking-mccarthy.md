# Plan: WRK-310 + WRK-311 — OrcFxAPI Schematic Capture & QTF Chart Improvements

## Context

Following the case 3.1 mesh visualization commit (`b3a4f29c`), two gaps remain:

1. **WRK-310**: The interactive Plotly Mesh3d works in a browser, but stakeholders viewing
   printed PDFs or slide decks need static images. OrcaWave's `OrcFxAPI.Diffraction` has
   **no** `SaveModelView()` — this task explores and implements the best available workaround.

2. **WRK-311**: The 4-panel QTF chart is working but not satisfying: the mean drift panel
   carries a spurious NaN imag trace, the comparison is diagonal-only, and there is no 2D
   QTF surface view. Validation narrative is generic.

---

## WRK-310: OrcFxAPI Schematic Capture

### Recommended Approach — Plotly Kaleido Static Export

The existing `_build_panel_mesh3d_html()` already constructs a full 3D Plotly figure with
three camera presets (Perspective, Plan, Elevation). The simplest and most reliable path is
to export that **same figure** to PNG using `kaleido` (already declared in `pyproject.toml`)
and embed the images as base64 in the report — no new GUI dependencies, no OrcaWave process
required.

#### Implementation Steps

**Step 1 — Add `save_mesh_views()` to `benchmark_plotter.py`**
- New static method on `BenchmarkPlotter`
- Signature: `save_mesh_views(fig: go.Figure, out_dir: Path) -> dict[str, Path]`
- For each camera dict (perspective, plan, elevation):
  - Call `fig.update_layout(scene_camera=camera)`
  - Call `fig.write_image(out_dir / f"mesh_{view}.png", scale=2)`
- Returns `{"perspective": Path, "plan": Path, "elevation": Path}`
- File: `src/digitalmodel/hydrodynamics/diffraction/benchmark_plotter.py`

**Step 2 — Update `build_mesh_schematic_html()` to embed static images**
- After calling `_build_panel_mesh3d_html()`, call `save_mesh_views()` into a temp dir
- Load each PNG → `img_to_base64()` pattern (same as `scripts/build_sme_report.py`)
- Prepend a `<div class="mesh-statics">` with three `<img>` tags (label + base64)
  **above** the interactive Plotly div

**Step 3 — Add `save_orcawave_views()` public helper to `mesh_capture.py` (new file)**
- Location: `src/digitalmodel/hydrodynamics/diffraction/mesh_capture.py`
- Function: `save_orcawave_views(owd_path: Path, out_dir: Path) -> dict[str, Path]`
- Orchestrates: load → build figure → `save_mesh_views()` → return paths
- This is the deliverable referenced in WRK-310

**Step 4 — Document in skill (v1.2.0 bump)**
- File: `workspace-hub/.claude/skills/engineering/marine-offshore/orcaflex-visualization/SKILL.md`
- Section: "OrcaWave Schematic Capture (Static PNG)"
- Note: `Diffraction` has no `SaveModelView`; Plotly+Kaleido is the primary path
- Note: `OrcaWaveScreenCapture` (win32gui/pyautogui) exists but is fragile — secondary
- Note: GDF→OrcaFlex `Model.SaveModelView()` loses free-surface zone — tertiary

#### Key Files

| File | Action |
|---|---|
| `src/digitalmodel/hydrodynamics/diffraction/benchmark_plotter.py` | Add `save_mesh_views()` static method |
| `src/digitalmodel/hydrodynamics/diffraction/mesh_capture.py` | NEW — `save_orcawave_views()` |
| `scripts/build_sme_report.py` | Reference for `img_to_base64()` pattern |
| `scripts/capture_riser_views.py` | Reference for `save_model_view()` BMP pattern |
| `src/.../orcawave/vision/screen_capture.py` | Document as secondary (fragile) approach |
| `workspace-hub/.claude/skills/.../orcaflex-visualization/SKILL.md` | v1.2.0 bump |

#### Verification
```
cd digitalmodel
python scripts/benchmark/run_benchmark.py --case 3.1
# → docs/.../3.1/benchmark/ should contain mesh_perspective.png, mesh_plan.png, mesh_elevation.png
# → benchmark_report.html section "Mesh Schematic" should show 3 static images above Plotly widget
```

---

## WRK-311: QTF Case 3.1 Chart Improvements

### Files Involved

| File | Role |
|---|---|
| `scripts/benchmark/qtf_postprocessing.py` | Main 4-panel QTF figure, lines 534–607 |
| `docs/modules/orcawave/L00_validation_wamit/3.1/digitized/*.csv` | WAMIT reference data |
| `docs/modules/orcawave/L00_validation_wamit/3.1/benchmark/benchmark_report.html` | Output |
| `src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py` | Report assembly |

### Change 1 — Fix Mean Drift Panel (NaN imag trace)

In `_build_sum_freq_figure()` (line ~580), the mean drift subplot receives both real and
imag traces from `_build_wamit_refs()`. Mean drift is purely real-valued.

- Filter: only add WAMIT traces to mean drift panel where `component == "real"`
- Drop imaginary OrcaWave trace for mean drift panel (all NaN — already noted in code)
- Update y-axis label: `"Mean Drift PI (kN/m²) — real component only"`

### Change 2 — Add 2D QTF Surface Heatmap (off-diagonal)

The Excel `.owr` output contains the full ω₁×ω₂ QTF matrix. Currently only the diagonal
(ω₁=ω₂) slice is plotted.

- In `_build_sum_freq_figure()`, after the 2×2 grid, assemble a new `go.Heatmap` figure
- Read QTF amplitude matrix: pivot the parsed DataFrame on `omega1` × `omega2` → amplitude
- Four heatmaps (mean drift, quadratic, direct potential, indirect potential) in 2×2 layout
- New function: `_build_qtf_heatmap_figure(qtf_data: pd.DataFrame) -> go.Figure`
- Embed as a second Plotly section in the QTF HTML block (below existing diagonal chart)

### Change 3 — Verify + Annotate WAMIT CSV Values

Current potential load CSV shows values up to 588 kN/m² (imag component). Before acting:
- Re-read the four CSV files; print value ranges
- Cross-check against WRK-311 open question: are these values correctly scaled?
- Add a `<!-- WAMIT digitization note -->` HTML comment in report section header explaining
  that markers are from digitized paper figures (approximate, ±5% read error)

### Change 4 — Case-Specific Validation Narrative

Replace or supplement the generic "Validation Notes & Potential Mismatch Sources" table:
- Add a case-3.1-specific paragraph after the QTF figure
- Content: confirm r=1.0000 is shape-correlation (not value-match), note mean drift is
  real-valued, note QTF is sum-frequency (not difference-frequency), note any frequency
  bands where OrcaWave and WAMIT diverge
- In `benchmark_runner.py` find the QTF section template and extend it

### Change 5 — Axis Labels and Tick Formatting (cosmetic)

In `_build_sum_freq_figure()`:
- X-axis: `"ω (rad/s)"` with `tickformat=".2f"`
- Y-axis per panel: include unit `(kN/m²)` and component (real/imag)
- Consistent y-axis range across real panels; independent range for imag panels
- WAMIT marker size: `marker_size=10` (currently default 6 — hard to see)

### Execution Order

1. Fix mean drift NaN trace (Change 1) — quickest, isolated
2. Axis/label improvements (Change 5) — cosmetic, isolated
3. WAMIT CSV verification (Change 3) — read-only, feeds into narrative
4. Validation narrative (Change 4) — prose addition
5. 2D QTF heatmap (Change 2) — new function, most effort

### Verification
```
cd digitalmodel
python scripts/benchmark/run_benchmark.py --case 3.1
# → benchmark_report.html:
#   - Mean drift panel: single real trace + WAMIT × markers (no NaN trace)
#   - 2D heatmap section visible below diagonal charts
#   - Axis labels show units and component names
#   - Case-specific narrative paragraph in QTF section
```

---

## Implementation Sequence (across both WRKs)

1. WRK-311 Changes 1, 5 (fast, chart fixes)
2. WRK-311 Changes 3, 4 (CSV verify + narrative)
3. WRK-311 Change 2 (2D heatmap — new function)
4. WRK-310 Steps 1, 2 (Kaleido export + embed in report)
5. WRK-310 Steps 3, 4 (public helper + skill update)
6. Regenerate report, commit, push

## Open Questions (to resolve before implementing WRK-311)

- Are the potential load CSV values (0–588 kN/m²) correct or mis-scaled? (User to confirm
  after reviewing paper Figures 33–34)
- Should the QTF section move earlier in the report (current: section 12)?
