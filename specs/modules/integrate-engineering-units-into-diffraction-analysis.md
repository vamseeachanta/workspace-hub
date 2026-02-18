---
title: "Integrate engineering units skill into diffraction analysis pipeline"
description: "Replace ad-hoc magic-number unit conversions with named, tested functions from a diffraction_units helper module"
version: "0.1.0"
module: hydrodynamics/diffraction
session:
  id: 2026-02-15-diffraction-units
  agent: claude-opus-4.6
review:
  status: draft
  reviewers: []
---

# Integrate Engineering Units into Diffraction Analysis

## Context

The `/units` skill (`assetutilities.units`) provides `TrackedQuantity`, `@unit_checked`, and a pint-backed registry. A bridge module exists at `digitalmodel/.../engineering_units.py`. However, the diffraction pipeline still uses ~30 ad-hoc conversions with magic numbers (`/ 1000.0`, `* 1000.0`, `2.0 * math.pi`, `np.degrees()`). These are the #1 source of unit-related bugs (e.g., the ISSC TLP 1000x inertia error).

**Goal**: Create a `diffraction_units.py` helper module with named, numpy-compatible conversion functions, then replace every magic-number conversion across the pipeline.

## Approach: Named Helper Functions (Phase 1)

Thin helper module with domain-specific named functions. No TrackedQuantity wrapping at call sites yet — that's a future phase. Functions accept and return raw floats/arrays for backward compatibility.

**Why not `@unit_checked` decorators now?** The pipeline works with numpy arrays and existing function signatures. Decorating functions requires restructuring signatures — separate, larger refactor. The helper module eliminates magic numbers immediately with zero risk.

## New Files

### 1. `src/digitalmodel/hydrodynamics/diffraction/diffraction_units.py` (~100 lines)

| Category | Functions |
|----------|-----------|
| **Mass** | `kg_to_tonnes(v)`, `tonnes_to_kg(v)` |
| **Density** | `density_kg_m3_to_t_m3(v)`, `density_t_m3_to_kg_m3(v)` |
| **Inertia** | `inertia_kg_m2_to_t_m2(v)`, `inertia_t_m2_to_kg_m2(v)` |
| **Frequency** | `hz_to_rad_per_s(v)`, `rad_per_s_to_hz(v)`, `rad_per_s_to_period_s(v)`, `period_s_to_rad_per_s(v)` |
| **Angle** | `radians_to_degrees(v)`, `degrees_to_radians(v)`, `complex_phase_degrees(v)` |

All functions: `ArrayLike -> ArrayLike` (scalar or numpy array).

### 2. `tests/hydrodynamics/diffraction/test_diffraction_units.py` (~120 lines)

Test classes: `TestMassConversions`, `TestDensityConversions`, `TestInertiaConversions`, `TestFrequencyConversions`, `TestAngularConversions`. Each covers scalars, arrays, roundtrips, and domain-meaningful values.

## Files to Modify (30 conversion sites)

### `orcawave_backend.py` (8 sites)

| Line | Before | After |
|------|--------|-------|
| 156 | `2.0 * math.pi / float(w)` | `rad_per_s_to_period_s(float(w))` |
| 181 | `spec.environment.water_density / 1000.0` | `density_kg_m3_to_t_m3(...)` |
| 196-201 | `t.get("Ixx", 0.0) / 1000.0` (×6) | `inertia_kg_m2_to_t_m2(...)` |
| 209 | `mass_kg / 1000.0` | `kg_to_tonnes(mass_kg)` |
| 287 | `inertia.mass / 1000.0` | `kg_to_tonnes(inertia.mass)` |

### `reverse_parsers.py` (5 sites)

| Line | Before | After |
|------|--------|-------|
| 256 | `f * 2.0 * math.pi` | `hz_to_rad_per_s(f)` |
| 477 | `float(water_density_raw) * 1000.0` | `density_t_m3_to_kg_m3(...)` |
| 507 | `2.0 * math.pi / float(t)` | `period_s_to_rad_per_s(float(t))` |
| 573, 659 | `mass_tonnes * 1000.0` | `tonnes_to_kg(mass_tonnes)` |
| 642-647 | `float(row0[0]) * 1000.0` (×6) | `inertia_t_m2_to_kg_m2(...)` |

### `report_generator.py` (4 sites)

| Line | Before | After |
|------|--------|-------|
| 313 | `np.degrees(roll_amp)` | `radians_to_degrees(roll_amp)` |
| 340 | `np.degrees(np.angle(...))` | `complex_phase_degrees(...)` |
| 568 | `np.degrees(amp)` | `radians_to_degrees(amp)` |
| 1653 | `2.0 * math.pi / tn` | `period_s_to_rad_per_s(tn)` |

### `orcawave_data_extraction.py` (1 site)

| Line | Before | After |
|------|--------|-------|
| 162 | `np.degrees(np.angle(rao_value))` | `complex_phase_degrees(rao_value)` |

### `validate_owd_vs_spec.py` (4 sites)

| Line | Before | After |
|------|--------|-------|
| 162 | `2.0 * np.pi * np.array(diff.frequencies)` | `hz_to_rad_per_s(np.array(...))` |
| 184 | `2.0 * np.pi / frequencies` | `rad_per_s_to_period_s(frequencies)` |
| 203 | `np.degrees(magnitude)` | `radians_to_degrees(magnitude)` |
| 207 | `np.degrees(np.angle(rao_complex))` | `complex_phase_degrees(rao_complex)` |

### Additional files (5 sites)

| File | Line | Before | After |
|------|------|--------|-------|
| `aqwa_backend.py` | 789 | `w / (2.0 * math.pi)` | `rad_per_s_to_hz(w)` |
| `orcaflex_exporter.py` | 187 | `2 * np.pi / freq` | `rad_per_s_to_period_s(freq)` |
| `orcaflex_exporter.py` | 222 | `2 * np.pi / freq` | `rad_per_s_to_period_s(freq)` |
| `benchmark_plotter.py` | 1970 | `2 * np.pi / max_pd_freq` | `rad_per_s_to_period_s(max_pd_freq)` |
| `cli.py` | 93-94 | `frequencies / (2 * np.pi)` | `rad_per_s_to_hz(frequencies)` |

### Excluded (not unit system boundaries)

- `orcawave_test_utilities.py` — `np.radians(heading)` calls are trigonometric computation in synthetic data generators, not cross-system unit conversions.

## Implementation Sequence (TDD)

| Step | Action | Gate |
|------|--------|------|
| 1 | Write `test_diffraction_units.py` | Tests fail (Red) |
| 2 | Write `diffraction_units.py` | Unit tests pass (Green) |
| 3 | Replace in `orcawave_backend.py` | `test_orcawave_backend.py` passes |
| 4 | Replace in `reverse_parsers.py` | `test_reverse_parsers.py` passes |
| 5 | Replace in `report_generator.py` | `test_report_generator.py` passes |
| 6 | Replace in remaining files | Full diffraction suite passes |
| 7 | Grep audit: zero remaining magic numbers | Confirmed clean |
| 8 | Commit | User approval |

## Verification

1. `uv run pytest tests/hydrodynamics/diffraction/test_diffraction_units.py -v` — all new tests pass
2. `uv run pytest tests/hydrodynamics/diffraction/ -v` — full suite passes (506+ tests)
3. Grep audit confirms no remaining `/ 1000.0`, `* 1000.0`, `2.0 * math.pi` in the diffraction package (excluding test utilities)

## Critical Files

| File | Role |
|------|------|
| `src/.../diffraction/diffraction_units.py` | **NEW** — all named conversion functions |
| `tests/.../diffraction/test_diffraction_units.py` | **NEW** — TDD test suite |
| `src/.../diffraction/orcawave_backend.py` | Highest conversion density (8 sites) |
| `src/.../diffraction/reverse_parsers.py` | Inverse conversions (5 sites) |
| `src/.../diffraction/report_generator.py` | Angular conversions (4 sites) |
| `scripts/benchmark/validate_owd_vs_spec.py` | Hz↔rad/s + angular (4 sites) |
| `src/.../diffraction/orcaflex_exporter.py` | Period conversions (2 sites) |
| `src/.../diffraction/aqwa_backend.py` | Frequency conversion (1 site) |
| `src/.../diffraction/benchmark_plotter.py` | Period conversion (1 site) |
| `src/.../diffraction/orcawave_data_extraction.py` | Phase extraction (1 site) |
| `src/.../diffraction/cli.py` | Frequency display (1 site) |
