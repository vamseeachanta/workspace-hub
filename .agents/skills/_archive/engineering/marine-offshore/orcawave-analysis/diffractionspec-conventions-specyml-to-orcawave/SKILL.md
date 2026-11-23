---
name: orcawave-analysis-diffractionspec-specyml-conventions
description: 'Sub-skill of orcawave-analysis: DiffractionSpec Conventions (spec.yml
  to OrcaWave).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# DiffractionSpec Conventions (spec.yml to OrcaWave)

## DiffractionSpec Conventions (spec.yml to OrcaWave)


The `DiffractionSpec` schema (`input_schemas.py`) is the canonical input format. Key conventions:

**Unit Handling:**
- Spec stores **pure SI** (kg, m, s, kg.m^2)
- `OrcaWaveBackend` divides mass, density, inertia by 1000 for OrcaFlex-SI (te)
- **EXCEPTION**: `external_damping` and `external_stiffness` 6x6 matrices pass through **without conversion** -- values must already be in OrcaFlex-SI units

**Mesh Paths:**
- `mesh_file` is relative to the spec.yml directory
- Runner copies mesh to output dir; backend strips to filename via `Path().name`
- **Known issue**: `_MESH_FORMAT_MAP` maps `dat` to `"Wamit dat"` -- AQWA .dat meshes need `"Aqwa dat"` but the enum lacks this variant

**Multi-Document YAML:**
- OrcaWave YAMLs have `%YAML 1.1` + `---` creating multi-doc streams
- Some files have UTF-8 BOM -- always use `encoding='utf-8-sig'` + `yaml.safe_load_all()`

**Canonical spec.yml Examples:**
- Barge: `docs/modules/orcawave/L02_barge_benchmark/spec.yml`
- Ship (QTF + roll damping): `docs/modules/orcawave/L03_ship_benchmark/spec.yml`
- Spar (rad/s freqs): `docs/modules/orcawave/L04_spar_benchmark/spec.yml`

**Frequency Input:**
- `input_type: period` -- values in seconds (backend uses directly)
- `input_type: frequency` -- values in rad/s (backend converts to periods via 2*pi/omega)
- OrcaWave always receives `WavesReferredToBy: "period (s)"`

---
