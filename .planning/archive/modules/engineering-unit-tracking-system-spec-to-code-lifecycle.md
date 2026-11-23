---
title: Engineering Unit Tracking System — Spec to Code Lifecycle
description: Unified unit tracking across engineering repos using pint, with provenance tracing from input config through computation to output
version: 0.1.0
module: engineering-units
work_item: WRK-095
session:
  id: cozy-whistling-micali
  agent: claude-opus-4.5
review:
  cross_review: pending
  iterations: 0
target_repos:
  - assetutilities (foundation)
  - digitalmodel (pilot)
  - worldenergydata (migration)
---

# Engineering Unit Tracking System

## Problem

Engineering calculations across `digitalmodel` and `worldenergydata` handle physical units inconsistently:

- **digitalmodel**: All calculations accept/return raw `float` values. A 30-line experimental `engineering_units.py` uses pint but creates a new `UnitRegistry()` on every decorator call (not a singleton). YAML configs declare units (`Units: inch`) but these are never enforced at runtime.
- **worldenergydata**: Hardcoded conversion factors in `constants.py` (376 lines, `EnergyUnits` enum + `UNIT_CONVERSIONS` dict). A separate `unit_converter.py` (402 lines) handles metocean conversions. No pint dependency.
- **No shared unit infrastructure** exists across repos despite `assetutilities` being a dependency of both.

## Solution

A shared `assetutilities.units` package built on `pint` that provides:

1. **Singleton registry** with custom engineering units (BOE, MCF, MMBTU, TOE, etc.)
2. **TrackedQuantity** — a pint Quantity wrapper with provenance chain
3. **Input parser** — converts YAML/JSON config values into tracked quantities
4. **Computation decorators** — `@unit_checked` that validates/converts inputs while remaining backward-compatible with raw floats
5. **Output formatter** — display formatting with unit conversion and audit trail export
6. **Domain packages** — energy, offshore, metocean unit mappings

## Architecture

```
assetutilities/src/assetutilities/units/
├── __init__.py              # Public API: get_registry, TrackedQuantity, unit_checked
├── registry.py              # Singleton pint.UnitRegistry + custom unit definitions
├── quantity.py              # TrackedQuantity with ProvenanceEntry chain
├── input_parser.py          # YAML/JSON → TrackedQuantity (unit system inference)
├── computation.py           # @unit_checked decorator for calculation functions
├── output_formatter.py      # Display formatting, audit trail export
├── traceability.py          # CalculationAuditLog aggregation
└── domains/
    ├── __init__.py
    ├── offshore.py          # Stress, force, pressure, length (Pa, psi, ksi, N, kN)
    ├── energy.py            # BOE, MCF, BTU, TOE — wraps worldenergydata constants
    └── metocean.py          # Speed, length, temp, pressure — wraps UnitConverter
```

### Why assetutilities?

- Already a dependency of both `digitalmodel` (pyproject.toml line 32) and `worldenergydata`
- Has no pint dependency today — adding it introduces zero conflicts
- Its `common/` directory already houses YAML loading and data utilities
- Avoids creating a new package with additional dependency coordination

### Why pint?

- Already installed in `digitalmodel` (used in `engineering_units.py`)
- Provides dimensional analysis, unit algebra, NumPy array support
- Custom unit registration via `ureg.define()` for industry units
- Well-maintained, standard Python unit library

## Key Design Decisions

### 1. Singleton Registry (Critical)

Multiple pint `UnitRegistry` instances cannot interoperate — quantities from different registries raise errors when combined. A single `get_registry()` singleton is mandatory.

**Current bug**: `engineering_units.py` creates `pint.UnitRegistry()` on every `@use_unit` call. This must be replaced.

### 2. Backward-Compatible Adoption

The `@unit_checked` decorator extracts `.magnitude` from `TrackedQuantity` before passing to function bodies. Existing call sites passing raw floats continue to work unchanged.

```python
# Before (no changes to function body):
def calc_buckling_stress(youngs_modulus: float, thickness: float, breadth: float):
    ...

# After (decorator added, body unchanged):
@unit_checked(youngs_modulus="Pa", thickness="m", breadth="m", _return="Pa")
def calc_buckling_stress(youngs_modulus, thickness, breadth):
    ...  # still receives floats internally
```

### 3. Coexistence with Hardcoded Conversions

`worldenergydata/common/constants.py` retains its `convert_units()` API. A `domains/energy.py` adapter wraps pint to match the same signature. Migration is per-module, not big-bang.

### 4. Provenance as Metadata, Not Per-Element

For NumPy array operations, provenance tracks at the array level (not per-element) to avoid performance overhead in fatigue/signal processing modules.

## Implementation Phases

### Phase 1: Foundation in assetutilities

**Create files:**
| File | Purpose |
|------|---------|
| `assetutilities/src/assetutilities/units/__init__.py` | Public API exports |
| `assetutilities/src/assetutilities/units/registry.py` | Singleton `get_registry()`, custom unit defs |
| `assetutilities/src/assetutilities/units/quantity.py` | `TrackedQuantity`, `ProvenanceEntry` |
| `assetutilities/src/assetutilities/units/traceability.py` | `CalculationAuditLog` |
| `assetutilities/tests/units/test_registry.py` | Registry + custom unit tests |
| `assetutilities/tests/units/test_quantity.py` | Quantity arithmetic + provenance tests |
| `assetutilities/tests/units/test_traceability.py` | Audit log tests |

**Modify:**
| File | Change |
|------|--------|
| `assetutilities/pyproject.toml` | Add `pint>=0.23,<1.0` to dependencies |

**Custom units to register:**
- Energy: BOE, MCF, MMCF, BCF, TCF, SCF, MMBTU, therm, TOE
- Offshore: ksi (1000 psi) — verify if pint already includes it
- All standard SI/Imperial units come from pint defaults

**Tests (TDD — write first):**
- Custom units resolve and convert correctly (BOE ↔ MMBTU, MCF ↔ BOE)
- Singleton returns same registry instance
- TrackedQuantity arithmetic propagates provenance
- Adding incompatible units raises `DimensionalityError`
- `float(tracked_quantity)` extracts magnitude

### Phase 2: Input/Output + Computation Layers

**Create files:**
| File | Purpose |
|------|---------|
| `assetutilities/src/assetutilities/units/input_parser.py` | `parse_config_value()`, `UNIT_SYSTEMS`, `FIELD_QUANTITY_MAP` |
| `assetutilities/src/assetutilities/units/computation.py` | `@unit_checked` decorator |
| `assetutilities/src/assetutilities/units/output_formatter.py` | `UnitFormatter`, audit trail export |
| `assetutilities/src/assetutilities/units/domains/__init__.py` | Domain package init |
| `assetutilities/src/assetutilities/units/domains/offshore.py` | Offshore field→quantity mappings |
| `assetutilities/src/assetutilities/units/domains/energy.py` | Pint-backed `convert_units()` adapter |
| `assetutilities/src/assetutilities/units/domains/metocean.py` | Pint-backed `UnitConverter` adapter |
| `assetutilities/tests/units/test_input_parser.py` | Config parsing tests |
| `assetutilities/tests/units/test_computation.py` | Decorator tests |
| `assetutilities/tests/units/test_output_formatter.py` | Formatting tests |
| `assetutilities/tests/units/test_domains_energy.py` | Compatibility vs hardcoded constants |
| `assetutilities/tests/units/test_domains_offshore.py` | Offshore unit mapping tests |

**Unit system mappings:**

```python
UNIT_SYSTEMS = {
    "inch": {"length": "inch", "stress": "psi", "pressure": "psi", "force": "lbf", ...},
    "SI":   {"length": "m",    "stress": "Pa",  "pressure": "Pa",  "force": "N", ...},
    "metric_engineering": {"length": "mm", "stress": "MPa", "force": "kN", ...},
}
```

**Compatibility tests (critical):**
- `domains/energy.py` must produce identical results to `worldenergydata/common/constants.py::convert_units()` for ALL existing conversion pairs
- `domains/metocean.py` must match `worldenergydata/metocean/processors/unit_converter.py` for all conversion methods
- Use `hypothesis` for property-based fuzz testing of conversion accuracy

### Phase 3: digitalmodel Pilot

**Target module**: `plate_buckling.py` — self-contained, 693 lines, clear physical parameters.

**Modify:**
| File | Change |
|------|--------|
| `digitalmodel/src/.../calculations/plate_buckling.py` | Add `@unit_checked` decorators to `ElasticBucklingCalculator` methods |
| `digitalmodel/src/.../common/engineering_units.py` | Replace with re-export from `assetutilities.units` |

**Create:**
| File | Purpose |
|------|---------|
| `digitalmodel/tests/.../test_plate_buckling_units.py` | Unit-tracking-specific integration tests |

**Validation**: All existing plate_buckling tests pass unchanged. New tests verify:
- Passing `TrackedQuantity(210e9, "Pa")` produces same result as `210e9` float
- Passing `TrackedQuantity(30e6, "psi")` auto-converts to Pa
- Mismatch (e.g., passing meters where Pa expected) raises error
- Output carries provenance chain from input through calculation

### Phase 4: worldenergydata Migration

**Modify:**
| File | Change |
|------|--------|
| `worldenergydata/src/.../common/constants.py` | Add deprecation wrapper on `convert_units()` delegating to `domains/energy.py` |
| `worldenergydata/src/.../metocean/processors/unit_converter.py` | Add deprecation wrapper delegating to `domains/metocean.py` |

No changes to `worldenergydata/pyproject.toml` — pint arrives transitively via `assetutilities`.

Old `EnergyUnits` enum and `UNIT_CONVERSIONS` dict remain importable for backward compatibility. Deprecation warnings log usage and recommend new API.

## Key Files Reference

| File | Repo | Lines | Role |
|------|------|-------|------|
| `infrastructure/common/engineering_units.py` | digitalmodel | 30 | Existing pint decorator (to replace) |
| `common/constants.py` | worldenergydata | 376 | Hardcoded energy conversions (to wrap) |
| `metocean/processors/unit_converter.py` | worldenergydata | 402 | Metocean conversions (to wrap) |
| `infrastructure/calculations/plate_buckling.py` | digitalmodel | 693 | Pilot calculation module |
| `infrastructure/base_configs/config_framework.py` | digitalmodel | ~200 | Config loader (integration point) |
| `pyproject.toml` | assetutilities | ~110 | Add pint dependency here |

## Audit Trail Example

For a plate buckling stress calculation reading from `pipe_py_8in_k2.yml`:

```
Provenance Trail:
  [2026-02-03T10:00:00] created: config/pipe_py_8in_k2.yml:E → psi
  [2026-02-03T10:00:01] converted: ElasticBucklingCalculator.calc → psi → Pa
  [2026-02-03T10:00:01] computed: calc_longitudinal_buckling_stress → Pa
  [2026-02-03T10:00:02] converted: display_formatting → Pa → MPa
```

Serializable to JSON for report generation or debugging.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Performance with large arrays | `@unit_checked` validates once at boundary; inner loops use raw floats. Provenance tracked per-array, not per-element |
| Circular deps (assetutilities ↔ consumer repos) | Domain packages define mappings generically; never import from digitalmodel/worldenergydata |
| pint version breaking changes | Pin `pint>=0.23,<1.0` for stable API |
| Serialization (TrackedQuantity through YAML/JSON) | Add `to_dict()`/`from_dict()` with unit string preservation |
| Adoption resistance | Fully backward-compatible — raw floats still work everywhere |

## Verification Plan

1. **Unit tests**: `uv run pytest assetutilities/tests/units/` — all registry, quantity, parser, computation, formatter, domain tests pass
2. **Compatibility tests**: `domains/energy.py` vs `constants.py` conversion parity; `domains/metocean.py` vs `UnitConverter` parity
3. **Integration test**: Full lifecycle — parse YAML config → TrackedQuantity → plate_buckling calculation → formatted output with audit trail
4. **Regression**: All existing tests in digitalmodel and worldenergydata continue passing (`uv run pytest` in each repo)
5. **Coverage**: 80% minimum per repo requirement; 100% on `registry.py` and `quantity.py`
