# OrcaFlex Modular Builder Enhancement Plan

> Granular, AI-friendly model generation with 1-to-1 YAML-to-OrcaFlex mapping

## Objective

Enhance the modular builder at `digitalmodel/src/digitalmodel/modules/orcaflex/modular_generator/` so that:
1. Every OrcaFlex concept (structure, environment, mooring, roller, vessel, constraint, etc.) has its own input YAML section with a **1-to-1 mapping** to the generated output
2. LLMs can define and vary any component via structured YAML without understanding OrcaFlex internals
3. The system starts with the existing pipeline installation example and extends incrementally

## Current State

- **10 builders** generating flat `includes/` files (01_general through 14_morison)
- **Single Pydantic schema** (`schema.py`, 849 lines) with `ProjectInputSpec` root model
- **Pipeline-only**: No support for vessels, moorings, constraints, winches, fenders
- **Ad-hoc context**: `Dict[str, Any]` for cross-builder entity sharing
- **No tests**: Zero test files for the modular generator
- **Working example**: 24-inch pipeline at `docs/modules/orcaflex/pipeline/installation/floating/24in_pipeline/manual/`

## Architecture Changes

### 1. Schema Package (replace `schema.py` monolith)

Split `schema.py` (849 lines) into `schema/` package with one module per concept:

```
modular_generator/schema/
  __init__.py          # Re-exports ProjectInputSpec
  _enums.py            # StructureType, WaveType, RampType, AnalysisType
  _compat.py           # Legacy pipeline/equipment -> granular transform
  _validators.py       # Cross-field validation functions
  metadata.py          # Metadata model
  environment.py       # WaterSpec, SeabedSpec, WaveTrainSpec, CurrentSpec, WindSpec
  variable_data.py     # CoatingSpec, DampingTableSpec, StiffnessTableSpec
  line_types.py        # HomogeneousPipeSpec, GeneralLineSpec
  lines.py             # LineSpec, ConnectionSpec, LineSegmentSpec, AttachmentSpec
  buoys.py             # Buoy6DSpec, Buoy3DSpec
  vessels.py           # VesselSpec, VesselTypeSpec, RAOSpec
  constraints.py       # ConstraintSpec, SpringCharacteristic
  simulation.py        # SimulationSpec, StageSpec
  installation.py      # InstallationSpec, PhaseSpec, StepSpec
  shapes.py            # ShapeSpec variants
  supports.py          # SupportTypeSpec
  morison.py           # MorisonTypeSpec
  groups.py            # GroupsSpec
  winches.py           # WinchSpec
  fenders.py           # FenderSpec, ForceDeflectionPoint
  links.py             # LinkSpec
  pipeline.py          # Legacy Pipeline model (backward compat)
  equipment.py         # Legacy Equipment model (backward compat)
  root.py              # ProjectInputSpec root with compat transforms
```

### 2. Enhanced Input Schema

The root `ProjectInputSpec` becomes composable -- each top-level key maps to one builder/output:

```yaml
metadata:           # -> identification
environment:        # -> 03_environment.yml
  water: {...}
  seabed: {...}
  waves: [{...}]    # list of wave trains (was single)
  current: {...}
  wind: {...}
variable_data:      # -> 02_var_data.yml
  coatings: [{...}]
  damping_tables: [{...}]
  stiffness_tables: [{...}]
line_types: [{...}] # -> 05_line_types.yml (explicit, not derived from pipeline)
support_types: [{...}] # -> 13_supports.yml
morison_types: [{...}] # -> 14_morison.yml
shapes: [{...}]     # -> 09_shapes.yml
buoys:              # -> 08_buoys.yml
  buoys_6d: [{...}]
  buoys_3d: [{...}]
vessels: [{...}]    # -> 04_vessels.yml (NEW)
lines: [{...}]      # -> 07_lines.yml (explicit, not derived)
constraints: [{...}] # -> 06_constraints.yml (NEW)
winches: [{...}]    # -> 11_winches.yml (NEW)
links: [{...}]      # -> 12_links.yml (NEW)
fenders: [{...}]    # -> 15_fenders.yml (NEW)
groups: {...}       # -> 10_groups.yml
simulation: {...}   # -> 01_general.yml
```

**Backward compatibility**: Legacy `pipeline` + `equipment` fields auto-transform via `model_validator(mode="before")` in `_compat.py`.

### 3. Builder Infrastructure

**Typed Context** (new `builders/context.py`):
```python
@dataclass
class BuilderContext:
    line_names: list[str]
    line_type_names: list[str]
    buoy_names_6d: list[str]
    buoy_names_3d: list[str]
    vessel_names: list[str]
    shape_names: list[str]
    constraint_names: list[str]
    support_type_names: list[str]
    coating_names: list[str]
    # ... typed fields replace Dict[str, Any]
```

**Builder Registry** (new `builders/registry.py`):
```python
@BuilderRegistry.register("03_environment.yml", order=30)
class EnvironmentBuilder(BaseBuilder):
    ...
```
Replaces hardcoded dict in `__init__.py`. Each builder self-registers with output file and dependency order.

**Enhanced BaseBuilder** (modify `builders/base.py`):
- Add `should_generate() -> bool` for conditional file generation
- Type `context` as `BuilderContext` instead of `Dict[str, Any]`

### 4. New Builders

| Builder | Output | Purpose |
|---------|--------|---------|
| `VesselsBuilder` | `04_vessels.yml` | Vessel types, RAOs, position/attitude |
| `ConstraintsBuilder` | `06_constraints.yml` | Spring, clamp, fixed constraints |
| `WinchesBuilder` | `11_winches.yml` | Winch connections, payout rates |
| `LinksBuilder` | `12_links.yml` | Rigid/flexible links |
| `FendersBuilder` | `15_fenders.yml` | Fender contact, force-deflection |

### 5. Existing Builder Modifications

| Builder | Change |
|---------|--------|
| `GeneralBuilder` | Accept `SimulationSpec` with analysis type field |
| `VarDataBuilder` | Accept expanded `VariableDataSpec` (damping/stiffness tables) |
| `EnvironmentBuilder` | Multi-wave-train list, seabed profile/3D mesh option |
| `LineTypeBuilder` | Accept explicit `LineTypeSpec[]` list instead of deriving from pipeline |
| `BuoysBuilder` | Accept explicit `Buoy6DSpec[]`/`Buoy3DSpec[]` instead of deriving from equipment |
| `LinesBuilder` | Accept explicit `LineSpec[]` list instead of deriving from pipeline |
| `ShapesBuilder` | Accept explicit `ShapeSpec[]` with all shape types |
| `SupportsBuilder` | Accept explicit `SupportTypeSpec[]` |
| `GroupsBuilder` | Accept explicit groups + auto-generate from registered entities |

## Scope: Phase 1 Only

**Goal**: Foundation refactoring -- restructure internals without breaking existing pipeline generation. Flat output (current format). Subsequent phases (granular inputs, vessels/moorings, multi-phase) follow in future sessions.

### Step-by-Step Implementation

1. **Write TDD anchor tests** against current 24in pipeline output
   - Generate output from existing spec, snapshot as golden reference
   - Test schema validation (valid + invalid inputs)
   - Test builder context entity passing

2. **Extract `schema.py` -> `schema/` package**
   - One module per concept (metadata, environment, variable_data, line_types, etc.)
   - `_enums.py` for all enumerations
   - `_compat.py` for legacy `pipeline`/`equipment` -> granular transform
   - `root.py` for `ProjectInputSpec` with `model_validator(mode="before")`
   - `__init__.py` re-exports `ProjectInputSpec`

3. **Create `BuilderContext` typed dataclass** (`builders/context.py`)
   - Typed fields: `line_names`, `line_type_names`, `buoy_names_6d`, `coating_names`, etc.
   - Replace `Dict[str, Any]` context in all builders

4. **Create `BuilderRegistry`** (`builders/registry.py`)
   - Decorator-based registration: `@BuilderRegistry.register("03_environment.yml", order=30)`
   - Auto-discovery replaces hardcoded dict in `__init__.py`

5. **Update `BaseBuilder`** (`builders/base.py`)
   - Add `should_generate() -> bool` for conditional file generation
   - Type `context` as `BuilderContext`

6. **Update `__init__.py` orchestrator** to use registry
   - Remove hardcoded `INCLUDE_ORDER` and builder dict
   - Use `BuilderRegistry.get_ordered_builders()`

7. **Update all 10 existing builders** to use `BuilderContext` type
   - Replace `self.context["key"]` with `self.context.key`
   - Replace `self._register_entity("key", val)` with `self.context.key = val`

8. **Verify all anchor tests pass** -- output identical to pre-refactoring

### Critical Files

| Action | File | Lines (est.) |
|--------|------|:---:|
| Delete | `modular_generator/schema.py` | 849 -> 0 |
| Create | `modular_generator/schema/__init__.py` | 30 |
| Create | `modular_generator/schema/_enums.py` | 80 |
| Create | `modular_generator/schema/_compat.py` | 150 |
| Create | `modular_generator/schema/_validators.py` | 100 |
| Create | `modular_generator/schema/metadata.py` | 50 |
| Create | `modular_generator/schema/environment.py` | 200 |
| Create | `modular_generator/schema/variable_data.py` | 80 |
| Create | `modular_generator/schema/line_types.py` | 100 |
| Create | `modular_generator/schema/lines.py` | 100 |
| Create | `modular_generator/schema/buoys.py` | 80 |
| Create | `modular_generator/schema/simulation.py` | 80 |
| Create | `modular_generator/schema/shapes.py` | 80 |
| Create | `modular_generator/schema/supports.py` | 60 |
| Create | `modular_generator/schema/morison.py` | 50 |
| Create | `modular_generator/schema/groups.py` | 40 |
| Create | `modular_generator/schema/pipeline.py` | 100 |
| Create | `modular_generator/schema/equipment.py` | 100 |
| Create | `modular_generator/schema/root.py` | 200 |
| Create | `builders/context.py` | 80 |
| Create | `builders/registry.py` | 100 |
| Modify | `builders/base.py` | 53 -> 65 |
| Modify | `__init__.py` | 118 -> 80 |
| Modify | each of 10 builders | minor context type changes |
| Create | `tests/.../conftest.py` | 150 |
| Create | `tests/.../test_backward_compat.py` | 150 |
| Create | `tests/.../test_schema_compat.py` | 200 |
| Create | `tests/.../test_builder_context.py` | 100 |
| Create | `tests/.../test_builder_registry.py` | 80 |
| Create | `tests/.../test_generator_integration.py` | 200 |

## Future Phases (not in this implementation)

- **Phase 2**: Granular input expansion (explicit line_types, lines, buoys sections)
- **Phase 3**: Vessels, constraints, moorings, winches, fenders, links
- **Phase 4**: Multi-phase installation, variant management

## Key Design Decisions

1. **Backward compat via transform**: `model_validator(mode="before")` auto-converts legacy format -> zero migration cost
2. **Typed context over dict**: Catches typos at registration time, IDE support
3. **Registry decorator**: Keeps builder registration co-located with class definition
4. **Conditional generation**: `should_generate()` means files only created when component data exists
5. **Explicit over derived**: New schema prefers explicit component lists; legacy pipeline format auto-derives them

## Input YAML Example (Phase 2 - Granular)

```yaml
metadata:
  name: "24in_pipeline_installation"
  structure: pipeline
  operation: installation/floating
  project: PROJ-001
  description: "24-inch pipeline floating installation"

environment:
  water:
    depth: 8
    density: 1.03
  seabed:
    slope: 0
    stiffness: {normal: 10000, shear: 100}
    friction: 0.3
  waves:
    - name: Wave1
      type: airy
      height: 0
      period: 8
      direction: 180
  current:
    speed: 1.0
    direction: 270
    profile: [[0, 1.0], [8, 0.8]]
  wind:
    speed: 8.87
    direction: 0

variable_data:
  coatings:
    - name: "3LPP+CWC80"
      layers: [{thickness: 0.0035, density: 1.1}, {thickness: 0.08, density: 3.0}]

line_types:
  - name: "X65+3LPP+CWC80"
    category: homogeneous_pipe
    od: 0.6096
    wall_thickness: 0.0222
    material: X65
    coating: "3LPP+CWC80"
    hydrodynamics: {cdn: 1.18, cdz: 0.008, can: 1.0}

shapes:
  - name: "Ramp inclined"
    type: block
    origin: [-126.35, -25, -5]
    size: [150, 50, 10]
    rotation: [0, 2.27, 0]

buoys:
  buoys_6d:
    - name: "Rollers"
      connection: fixed
      position: [100, 0, 0]
      mass: 0
      volume: 0
      supports:
        line: "24'' Line"
        type: "Support type2"
        positions: [[17.5, 3.5, -1.6], [-21.5, 2.5, -1.6]]
    - name: "Tug1"
      connection: fixed
      position: [100, 0, 0]
      mass: 200
      volume: 235

lines:
  - name: "24'' Line"
    connections:
      end_a: {type: fixed, position: [-101, 0, 4.505]}
      end_b: {type: "6D buoy1", position: [0, 0, 0]}
    segments:
      - {line_type: "X65+3LPP+CWC80", length: 600, target_segment_length: 5}
    attachments:
      - {type: "BM", spacing: 12, start: 0, end: 600}

simulation:
  time_step: 0.1
  stages: [8, 16]
  north_direction: 70
```

## Testing Strategy

### TDD Anchors (write first, Phase 1)

1. **`test_backward_compat.py`**: Load existing 24in pipeline spec -> generate output -> verify structure matches current output
2. **`test_schema_compat.py`**: Legacy `pipeline` + `equipment` format parses into new schema without errors
3. **`test_builder_context.py`**: Typed entity registration, reject unknown keys
4. **`test_builder_registry.py`**: Ordering, discovery, conditional generation

### Unit Tests (per builder)

One test file per builder verifying:
- Correct OrcaFlex YAML structure generated
- Entity registration into context
- `should_generate()` returns False when no data

### Integration Tests

1. **Round-trip**: Legacy spec -> generate -> compare with manual output
2. **Explicit spec**: Granular spec -> generate -> validate OrcaFlex YAML
3. **CLI**: `validate` and `generate` commands produce correct output

### Test Location

```
tests/modules/orcaflex/modular_generator/
  conftest.py                      # Shared fixtures, sample specs
  fixtures/                        # Sample YAML inputs
    pipeline_simple.yml
    pipeline_granular.yml
    mooring_simple.yml
  test_schema_compat.py
  test_builder_context.py
  test_builder_registry.py
  test_backward_compat.py
  test_general_builder.py
  test_environment_builder.py
  test_vardata_builder.py
  test_linetype_builder.py
  test_buoys_builder.py
  test_lines_builder.py
  test_shapes_builder.py
  test_groups_builder.py
  test_generator_integration.py
```

### Verification

```bash
# Run all modular generator tests
cd /mnt/github/workspace-hub/digitalmodel
uv run pytest tests/modules/orcaflex/modular_generator/ -v

# Generate from legacy spec (backward compat)
uv run python -m digitalmodel.modules.orcaflex.modular_generator generate \
  --input docs/modules/orcaflex/pipeline/installation/floating/24in_pipeline/spec.yml \
  --output /tmp/test_output

# Generate from granular spec
uv run python -m digitalmodel.modules.orcaflex.modular_generator generate \
  --input tests/modules/orcaflex/modular_generator/fixtures/pipeline_granular.yml \
  --output /tmp/test_granular

# Verify output structure
ls -la /tmp/test_output/includes/
diff /tmp/test_output/includes/01_general.yml /tmp/test_granular/includes/01_general.yml
```
