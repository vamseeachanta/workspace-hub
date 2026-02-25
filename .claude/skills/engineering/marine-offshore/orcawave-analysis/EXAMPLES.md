# OrcaWave Examples — Quick Reference (L01–L06)

> Maps the 6 official OrcaWave examples to skills and API patterns.
> Examples live in `digitalmodel/docs/domains/orcawave/examples/`.

## At a Glance

| # | Name | Bodies | Solver | Key Feature | Skills |
|---|------|--------|--------|-------------|--------|
| L01 | Default vessel | 1 | Potential + Source | Control surface mean drift | `orcawave-analysis` |
| L02 | OC4 Semi-sub | 1 | Potential + Source | Morison drag linearisation | `orcawave-damping-sweep` |
| L03 | Semi-sub multibody | 4 | Potential + Source | Body hierarchy, coupling | `orcawave-multi-body` |
| L04 | Sectional bodies | 7 | Potential only | Sectional stiffness method | `orcawave-analysis` |
| L05 | Panel pressures | 7 | Potential only | `OutputPanelPressures: Yes` | `orcawave-analysis` |
| L06 | Full QTF | 1 | Full QTF (restart) | Second-order QTF, restart from .owd | `orcawave-qtf-analysis` |

## Example Profiles

### L01 — Default Vessel
**Purpose**: Baseline single-body with control surface for accurate mean drift.
- `SolveType: Potential and source formulations`
- `LinearSolverMethod: Direct LU`
- `BodyControlSurfaceType: Defined by mesh file` — control surface improves mean drift accuracy
- 24 periods (4–22 s), 9 headings (0–180°)
- Water depth: 400 m

### L02 — OC4 Semi-sub
**Purpose**: Semi-submersible with Morison drag linearisation.
- `LinearSolverMethod: Iterative AGS` (large panel count)
- `HasWaveSpectrumForDragLinearisation: Yes` — JONSWAP spectrum for drag linearisation
- `QuadraticLoadControlSurface: No` — pressure integration method instead
- 32 periods, 9 headings; water depth: 200 m
- Morison elements: 4 types (UC, BC, MC, Pontoon)

### L03 — Semi-sub Multibody
**Purpose**: 4-body analysis with body connection hierarchy.
- Same base setup as L02 (drag linearisation, JONSWAP)
- `BodyConnectionParent` hierarchy: 3 offset columns → Centre column
- 16 headings (full 360° coverage in 22.5° steps)
- `addedMass` shape: `(nfreq, 24, 24)` — extract body block `[r0:r0+6, c0:c0+6]`

### L04 — Sectional Bodies
**Purpose**: Multi-body assembly with sectional hydrostatics.
- `SolveType: Potential formulation only` — no source formulation
- `BodyHydrostaticIntegralMethod: Analytic` (vs Standard in L01–L03)
- `BodyHydrostaticStiffnessMethod: Sectional` — bodies computed as sections of parent
- 7 bodies: Keystone → 3 × (Pontoon → Column)
- 31 periods including ultra-long (4–600 s)

### L05 — Panel Pressures
**Purpose**: Identical to L04 with panel pressure output enabled.
- `OutputPanelPressures: Yes` — enables per-panel pressure in results
- `OutputIntermediateResults: Yes` — saves intermediate convergence data
- Access via `diff.panelGeometry` iterator (dict keys: `centroid`, `area`, `objectName`)

### L06 — Full QTF
**Purpose**: Second-order full QTF computation via restart from parent model.
- `RestartingFrom: <parent>.owd` — restarts from existing binary (does NOT re-solve first order)
- `SolveType: Full QTF calculation`
- QTF params: `QTFMinPeriodOrFrequency`, `QTFMaxPeriodOrFrequency`, `QTFFrequencyTypes`
- Free surface zone: panelled inner zone + quadrature outer zone
- Two YML files: L06A (automatically generated free surface) and L06B (mesh file free surface)

## Key API Patterns

```python
import OrcFxAPI

# Load .owr results (all examples)
diff = OrcFxAPI.Diffraction("path/to/example.owr")

# Frequencies: Hz, descending order — always sort ascending
freqs_hz = np.array(diff.frequencies)
sort_idx = np.argsort(freqs_hz)         # ascending
periods = 1.0 / freqs_hz[sort_idx]

# RAO shape: (nheading, nfreq, 6) single-body | (nheading, nfreq, 12) 2-body
raos = diff.displacementRAOs            # complex array
rao_mag = np.abs(raos)[:, sort_idx, :] # sorted ascending

# Multi-body added mass: (nfreq, 6N, 6N)
am = diff.addedMass
n_bodies = am.shape[1] // 6            # infer body count
body_block = am[:, 0:6, 0:6]          # body 0 self-influence

# Rotational RAOs in rad/m — convert for display
import numpy as np
rao_rot_degm = np.abs(raos[:, :, 3:6]) * (180.0 / np.pi)
```

## Parameter Reference

See `PARAMETER_REFERENCE.md` in this folder for the full cross-example parameter table.

## Run Scripts

Each example folder contains `run_orcawave.py` (L02–L06) or
`run_orcawave_diffraction_improved.py` (L01).

---
*WRK-320 (2026-02-24) — derived from WRK-317 parameter audit and L01–L06 analysis*
