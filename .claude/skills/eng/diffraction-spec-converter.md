# Diffraction Spec Converter Skill

**Skill name**: `diffraction_spec_converter`
**Module path**: `src/digitalmodel/hydrodynamics/diffraction/`
**WRK**: WRK-240
**Updated**: 2026-02-20
**Status**: production

---

## Overview

The diffraction spec converter provides three workflows:

1. **Forward**: `spec.yml` (canonical DiffractionSpec) → AQWA deck input (`.dat`) or OrcaWave YAML input
2. **Forward (OrcaFlex export)**: solver results (`DiffractionResults`) → OrcaFlex vessel type, RAO CSV, added-mass/damping CSV, Excel workbook
3. **Reverse**: AQWA `.dat` or OrcaWave `.yml` input files → `DiffractionSpec` (spec.yml round-trip); AQWA `.lis` result file → unified `DiffractionResults` schema

The central schema object `DiffractionSpec` (Pydantic BaseModel) is solver-agnostic and lives in `input_schemas.py`. All backends consume it.

---

## Key Classes and Functions

### `input_schemas.py` — canonical input schema

| Class | Purpose |
|---|---|
| `DiffractionSpec` | Root spec model. `from_yaml(path)` loads; `to_yaml(path)` dumps; `get_bodies()` returns list of `BodySpec`. |
| `BodySpec` | Per-body container: `vessel` (`VesselSpec`), `solver_options`, `output`. |
| `VesselSpec` | Vessel metadata: `name`, `type`, `geometry` (`VesselGeometry`), `inertia` (`VesselInertia`). |
| `VesselGeometry` | `mesh_file`, `mesh_format` (`MeshFormatType`), `symmetry` (`SymmetryType`), `reference_point`. |
| `VesselInertia` | `mass`, `cog`, `rog` (radii of gyration), optional `added_mass_matrix`, `damping_matrix`, `stiffness_matrix`. |
| `EnvironmentSpec` | `water_depth` (float or `"infinite"`), `water_density`, `gravitational_acceleration`. |
| `FrequencySpec` | `values` list or `range` (`FrequencyRangeSpec`). `.to_frequencies_rad_s()` and `.to_periods_s()` resolve to concrete lists. |
| `WaveHeadingSpec` | `values` list or `range` (`HeadingRangeSpec`). `.to_heading_list()` resolves. |
| `SolverOptions` | `analysis_type` (`AnalysisType` enum), `precision` (`SolverPrecision`), `qtf_calculation`, `damping_lid` (`DampingLidSpec`). |
| `AnalysisType` | Enum: `radiation`, `diffraction`, `frequency_domain`, `full_qtf`. |
| `MetadataSpec` | `project`, `vessel_name`, `analyst`, `date`, `revision`. |

### `spec_converter.py` — forward workflow entry point

```
digitalmodel.hydrodynamics.diffraction.spec_converter.SpecConverter
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(spec_path: Path)` | Loads and validates `DiffractionSpec` from YAML. Raises on parse/schema error. |
| `convert` | `(solver, format="single", output_dir=Path("output")) -> Path` | Converts to one solver. `solver` is `"aqwa"` or `"orcawave"`. `format` is `"single"` or `"modular"`. |
| `convert_all` | `(format="single", output_dir=Path("output")) -> dict[str, Path]` | Converts to all registered solvers; creates per-solver subdirs. |
| `validate` | `() -> list[str]` | Returns list of semantic issues (empty = valid). Checks mesh file presence, non-empty frequencies/headings, positive mass. |

### `aqwa_backend.py` — AQWA input generation

```
digitalmodel.hydrodynamics.diffraction.aqwa_backend.AQWABackend
```

| Method | Signature | Returns |
|---|---|---|
| `generate_single` | `(spec: DiffractionSpec, output_dir: Path) -> Path` | Writes one `.dat` file with all decks concatenated. |
| `generate_modular` | `(spec: DiffractionSpec, output_dir: Path) -> Path` | Writes one file per AQWA deck section. |
| `build_deck0` | `(spec) -> list[str]` | AQWA DECK 0 (job title, OPTIONS, RESTART). |
| `build_deck1` | `(spec) -> list[str]` | DECK 1 (geometry coordinates and panels). |
| `build_deck2` | `(spec) -> list[str]` | DECK 2 (structural/mesh data). |
| `build_deck3..8` | `(spec) -> list[str]` | Remaining AQWA decks. |

### `orcawave_backend.py` — OrcaWave input generation

```
digitalmodel.hydrodynamics.diffraction.orcawave_backend
```

Module-level functions build each YAML section: `_build_general_section`, `_build_environment_section`, `_build_bodies_section`, `_build_frequencies_section`, `_build_headings_section`, `_build_solver_section`, `_build_outputs_section`, `_build_damping_lid_section`, `_build_qtf_section`.

### `reverse_parsers.py` — reverse workflow (input files → DiffractionSpec)

```
digitalmodel.hydrodynamics.diffraction.reverse_parsers
```

| Class | Parses | Method |
|---|---|---|
| `AQWAInputParser` | AQWA `.dat` input file | `.parse(dat_path: Path) -> DiffractionSpec` |
| `OrcaWaveInputParser` | OrcaWave `.yml` input | `.parse(yml_path: Path) -> DiffractionSpec` |

### `aqwa_lis_parser.py` — AQWA result extraction (reverse, results → unified schema)

```
digitalmodel.hydrodynamics.diffraction.aqwa_lis_parser
```

| Symbol | Type | Purpose |
|---|---|---|
| `AQWALISParser` | Class | Low-level `.lis` parser. `__init__(lis_file_path)`. Methods: `parse_all()`, `parse_rao_table()`, `parse_added_mass_table()`, `parse_damping_table()`, `extract_frequencies_and_periods()`, `extract_headings()`. |
| `parse_aqwa_lis_file(path)` | Function | Convenience wrapper → `dict` of raw parsed data. |
| `extract_aqwa_frequencies(path)` | Function | Returns `(freqs_rad_s, periods_s)` tuple. |
| `extract_aqwa_headings(path)` | Function | Returns `list[float]` of headings in degrees. |
| `extract_aqwa_raos(path)` | Function | Returns nested dict keyed by `(freq, heading)`. |
| `extract_aqwa_added_mass(path)` | Function | Returns `dict[float, np.ndarray]` (freq → 6x6 matrix). |
| `extract_aqwa_damping(path)` | Function | Returns `dict[float, np.ndarray]` (freq → 6x6 matrix). |

### `aqwa_converter.py` — AQWA results → unified DiffractionResults

```
digitalmodel.hydrodynamics.diffraction.aqwa_converter.AQWAConverter
```

`__init__(analysis_folder: Path, vessel_name: str)` — converter entry point. Reads `.lis` files from folder and converts to `DiffractionResults`.

### `orcaflex_exporter.py` — results → OrcaFlex format (forward, results export)

```
digitalmodel.hydrodynamics.diffraction.orcaflex_exporter.OrcaFlexExporter
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(results: DiffractionResults, output_dir: Path)` | — |
| `export_all` | `() -> dict[str, Path]` | Exports all formats; returns name→path mapping. |
| `export_vessel_type` | `() -> Path` | OrcaFlex VesselType YAML. |
| `export_raos_csv` | `() -> Path` | RAO amplitude+phase per DOF CSV. |
| `export_added_mass_csv` | `() -> Path` | Added mass matrix CSV. |
| `export_damping_csv` | `() -> Path` | Radiation damping matrix CSV. |
| `export_excel_workbook` | `() -> Path` | Excel workbook with summary, RAO, added mass, damping, and discretization sheets. |
| `export_summary_report` | `() -> Path` | HTML or text summary report. |

### `output_schemas.py` — unified result data structures

```
digitalmodel.hydrodynamics.diffraction.output_schemas
```

Key dataclasses: `DiffractionResults`, `RAOSet`, `RAOComponent`, `AddedMassSet`, `DampingSet`, `HydrodynamicMatrix`, `FrequencyData`, `HeadingData`, `DOF` (enum), `Unit` (enum).

---

## Workflow 1: Forward — spec.yml → AQWA or OrcaWave input

```python
from pathlib import Path
from digitalmodel.hydrodynamics.diffraction.spec_converter import SpecConverter

# Load spec
converter = SpecConverter(Path("analysis.yml"))

# Validate before converting
issues = converter.validate()
if issues:
    for issue in issues:
        print(f"WARN: {issue}")

# Convert to AQWA (single .dat file)
aqwa_dat = converter.convert(solver="aqwa", format="single", output_dir=Path("out/aqwa"))

# Convert to OrcaWave (.yml)
orcawave_yml = converter.convert(solver="orcawave", format="single", output_dir=Path("out/orcawave"))

# Convert to all solvers at once
all_outputs = converter.convert_all(format="single", output_dir=Path("out"))
# Returns: {"aqwa": Path("out/aqwa/vessel_name.dat"), "orcawave": Path("out/orcawave/vessel_name.yml")}
```

---

## Workflow 2: Forward — DiffractionResults → OrcaFlex export

```python
from pathlib import Path
from digitalmodel.hydrodynamics.diffraction.aqwa_converter import AQWAConverter
from digitalmodel.hydrodynamics.diffraction.orcaflex_exporter import OrcaFlexExporter

# Convert AQWA results folder to unified schema
converter = AQWAConverter(
    analysis_folder=Path("aqwa_results/"),
    vessel_name="FPSO_Alpha"
)
results = converter.convert_to_unified_schema()

# Export to OrcaFlex formats
exporter = OrcaFlexExporter(results=results, output_dir=Path("orcaflex_export/"))
paths = exporter.export_all()
# paths: {"vessel_type": ..., "raos_csv": ..., "added_mass_csv": ..., "damping_csv": ..., "excel": ..., "report": ...}

# Or export individual formats
vessel_type_path = exporter.export_vessel_type()   # VesselType YAML
raos_path = exporter.export_raos_csv()             # RAO amplitude + phase
excel_path = exporter.export_excel_workbook()      # Excel workbook
```

---

## Workflow 3: Reverse — AQWA .lis result → unified schema

```python
from pathlib import Path
from digitalmodel.hydrodynamics.diffraction.aqwa_lis_parser import (
    AQWALISParser,
    parse_aqwa_lis_file,
    extract_aqwa_frequencies,
    extract_aqwa_raos,
)

lis_path = Path("analysis.lis")

# High-level: parse everything at once
parser = AQWALISParser(lis_path)
raw = parser.parse_all()
# raw keys: "frequencies_rad_s", "periods_s", "headings_deg",
#           "raos", "added_mass", "damping"

# Convenience functions for targeted extraction
freqs_rad, periods = extract_aqwa_frequencies(lis_path)
raos = extract_aqwa_raos(lis_path)
# raos[(freq_rad, heading_deg)] -> {"surge": (amplitude, phase), "sway": ..., ...}
```

---

## Workflow 4: Reverse — parse legacy AQWA input → spec.yml

```python
from pathlib import Path
from digitalmodel.hydrodynamics.diffraction.reverse_parsers import AQWAInputParser

parser = AQWAInputParser()
spec = parser.parse(Path("legacy_model.dat"))

# Round-trip: save as spec.yml
spec.to_yaml(Path("legacy_model_spec.yml"))
```

---

## Workflow 5: Reverse — parse legacy OrcaWave input → spec.yml

```python
from pathlib import Path
from digitalmodel.hydrodynamics.diffraction.reverse_parsers import OrcaWaveInputParser

parser = OrcaWaveInputParser()
spec = parser.parse(Path("existing_orcawave_run.yml"))

# Convert to AQWA (now round-trippable)
from digitalmodel.hydrodynamics.diffraction.spec_converter import SpecConverter
spec.to_yaml(Path("round_trip.yml"))
converter = SpecConverter(Path("round_trip.yml"))
aqwa_dat = converter.convert(solver="aqwa", output_dir=Path("out/aqwa"))
```

---

## Input Schema (spec.yml structure)

```yaml
version: "1.0"
analysis_type: diffraction        # radiation | diffraction | frequency_domain | full_qtf
metadata:
  project: "My Project"
  vessel_name: "FPSO Alpha"
  analyst: "J. Smith"
  date: "2026-02-20"

vessel:
  name: "FPSO_Alpha"
  type: "FPSO"
  geometry:
    mesh_file: "hull.gdf"
    mesh_format: GDF               # GDF | DAT | STL | MSH
    symmetry: none                 # none | xz | yz | double
    reference_point: [0.0, 0.0, 0.0]
  inertia:
    mass: 1.2e8                    # kg
    cog: [0.0, 0.0, -5.0]         # m from reference point
    rog: [25.0, 60.0, 60.0]       # radii of gyration (m): Kxx, Kyy, Kzz

environment:
  water_depth: 200.0              # m, or "infinite"
  water_density: 1025.0           # kg/m^3
  gravitational_acceleration: 9.81

frequencies:
  range:
    start: 0.2                    # rad/s
    end: 2.0
    count: 20
  # OR explicit list:
  # values: [0.2, 0.4, 0.6, ...]
  # input_type: angular_frequency  # angular_frequency | period

wave_headings:
  range:
    start: 0.0                    # degrees
    end: 180.0
    step: 45.0
  # OR explicit list:
  # values: [0, 45, 90, 135, 180]

solver_options:
  precision: double               # single | double
  qtf_calculation: false
  damping_lid:
    enabled: false

outputs:
  formats: [aqwa, orcawave]
  components: [raos, added_mass, damping]
```

---

## Output Schema (DiffractionResults)

```
DiffractionResults
├── vessel_name: str
├── source_file: str
├── frequencies: FrequencyData
│   ├── values_rad_s: list[float]
│   └── values_hz: list[float]
├── headings: HeadingData
│   └── values_deg: list[float]
├── raos: RAOSet
│   ├── surge: RAOComponent  (dof=DOF.SURGE)
│   │   ├── magnitudes: dict[(freq, heading), float]
│   │   └── phases_deg: dict[(freq, heading), float]
│   ├── sway, heave, roll, pitch, yaw: RAOComponent
├── added_mass: AddedMassSet
│   └── matrices: dict[float, HydrodynamicMatrix]  # freq -> 6x6
├── damping: DampingSet
│   └── matrices: dict[float, HydrodynamicMatrix]  # freq -> 6x6
└── metadata: dict
```

---

## Test coverage

| Test file | Tests |
|---|---|
| `tests/hydrodynamics/diffraction/test_spec_converter.py` | SpecConverter forward workflow |
| `tests/hydrodynamics/diffraction/test_input_schemas.py` | DiffractionSpec validation |
| `tests/hydrodynamics/diffraction/test_aqwa_backend.py` | AQWABackend deck generation |
| `tests/hydrodynamics/diffraction/test_aqwa_backend_damping.py` | AQWA damping deck |
| `tests/hydrodynamics/diffraction/test_aqwa_parser.py` | AQWALISParser |
| `tests/hydrodynamics/diffraction/test_aqwa_result_extractor.py` | AQWA result extraction |
| `tests/hydrodynamics/diffraction/test_orcawave_backend.py` | OrcaWaveBackend |
| `tests/hydrodynamics/diffraction/test_reverse_parsers.py` | AQWAInputParser / OrcaWaveInputParser |

Total diffraction module test files: 26. Total diffraction tests: ~566.

---

## Related skills

- `.claude/skills/diffraction-analysis/SKILL.md` — broad diffraction workflow (AQWA, OrcaWave, BEMRosetta)
- `.claude/skills/aqwa-analysis/SKILL.md` — AQWA-specific result extraction
- `.claude/skills/orcawave-analysis/SKILL.md` — OrcaWave run configuration and QTF
- `.claude/skills/orcawave-aqwa-benchmark/SKILL.md` — cross-solver comparison framework
- `.claude/skills/orcawave-to-orcaflex/SKILL.md` — OrcaWave → OrcaFlex export

---

## Known limitations

1. `OrcaWaveBackend` hardcodes `SolveType = "Potential and source formulations"` regardless of `qtf_calculation` flag in the spec (`orcawave_backend.py:333`). Full QTF runs require manual override.
2. `AQWABackend` hardcodes `RESTART 1 5` even when `qtf_calculation: true` (`aqwa_backend.py:412`). Full QTF requires `RESTART 1 8` — must set manually after generation.
3. `SolverOptions.qtf_calculation` (bool) cannot represent OrcaWave's 6 SolveType levels. Use solver options cross-reference in `diffraction-analysis` skill for mapping.
