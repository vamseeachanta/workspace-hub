---
name: diffraction-analysis-canonical-specyml-format-diffractionspec
description: 'Sub-skill of diffraction-analysis: Canonical spec.yml Format (DiffractionSpec).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Canonical spec.yml Format (DiffractionSpec)

## Canonical spec.yml Format (DiffractionSpec)


All diffraction analyses should be driven by a `spec.yml` conforming to `DiffractionSpec` (`input_schemas.py`). This is the solver-agnostic input that both OrcaWave and AQWA backends consume.

**Template structure:** `version`, `analysis_type`, `vessel` (name/type/geometry/inertia), `environment`, `frequencies`, `wave_headings`, `solver_options`, `outputs`, `metadata`.

**Live examples:**
- `docs/modules/orcawave/L02_barge_benchmark/spec.yml` -- standard diffraction
- `docs/modules/orcawave/L03_ship_benchmark/spec.yml` -- full QTF + external roll damping
- `docs/modules/orcawave/L04_spar_benchmark/spec.yml` -- rad/s frequency input

**Critical unit rule:** Spec uses pure SI (kg, m, s). Backends convert. But `external_damping`/`external_stiffness` matrices pass through without conversion -- see `orcawave-analysis` skill for details.
