# fluids Library Evaluation — Piping Design Integration

**Date:** 2026-03-30
**Issue:** vamseeachanta/workspace-hub#1450
**Version evaluated:** 1.3.0 (released 2025-10-25)
**Parent issue:** #1397 (OSS Engineering Catalog)

## Summary

fluids is a pure-Python fluid dynamics library by Caleb Bell, part of the Chemical Engineering Design Library (ChEDL) ecosystem. It implements engineering standards correlations for piping design (Crane TP-410, API 520/521, ASME), friction factors, fittings, valves, compressible flow, and relief valve sizing. MIT licensed, 423 stars, zero compiled dependencies. The API surface is well-organized into domain-specific modules with consistent SI-unit conventions. Strong fit for digitalmodel piping workflow integration.

---

## Module Inventory

| Module | Domain | Key Functions |
|---|---|---|
| `fluids.friction` | Friction factors | `friction_factor()` — Colebrook, Churchill, Swamee-Jain, others |
| `fluids.fittings` | Fittings K-factors | `bend_rounded()`, `entrance_sharp()`, `exit_normal()`, `K_from_f()`, Crane/Rennels/Idelchik methods |
| `fluids.piping` | Pipe schedules | `nearest_pipe()` — ANSI/ASME pipe schedule lookup |
| `fluids.safety_valve` | Relief valve sizing | `API520_A_g()`, `API520_A_steam()`, `API520_A_l()` — API 520 Part 1 |
| `fluids.compressible` | Compressible flow | `isothermal_gas()`, `isentropic()`, `Panhandle_A/B()` |
| `fluids.control_valve` | Control valves | ISA/IEC sizing per IEC 60534 |
| `fluids.flow_meter` | Orifice/flow meters | ISO 5167 orifice, Venturi, cone, wedge meters |
| `fluids.core` | Dimensionless numbers | `Reynolds()`, `Prandtl()`, `Bond()`, `Froude()`, etc. |
| `fluids.two_phase` | Two-phase flow | Lockhart-Martinelli, Beggs-Brill, homogeneous models |
| `fluids.drag` | Drag/terminal velocity | Sphere drag, particle settling |
| `fluids.atmosphere` | Atmospheric models | US Standard Atmosphere 1976, wind models |
| `fluids.geometry` | Tank/vessel geometry | Tank volume, head geometry (ASME flanged & dished, etc.) |
| `fluids.packed_bed` | Packed beds | Ergun equation, packed tower pressure drop |
| `fluids.filters` | Filter pressure drop | Various filter correlations |
| `fluids.jet_pump` | Ejectors | Jet pump sizing and rating |
| `fluids.mixing` | Mixing | Impeller correlations |
| `fluids.open_flow` | Open channel | Manning, Chezy, weir calculations |
| `fluids.pump` | Pumps | Affinity laws, NPSH, specific speed |
| `fluids.separator` | Separators | Stokes settling, separator sizing |

---

## Standards Coverage

| Standard | Module | Coverage |
|---|---|---|
| Crane TP-410 | `fittings`, `friction` | Fittings K-factors, equivalent length method, pipe friction |
| API 520 Part 1 | `safety_valve` | Gas, steam, and liquid relief valve area sizing (4 formulas: metric + imperial, viscosity units) |
| API 521 | `safety_valve` | Fire-case relief scenarios (partial) |
| ASME B36.10/B36.19 | `piping` | Standard pipe schedules, nearest-pipe lookup |
| ISO 5167 | `flow_meter` | Orifice plate, flow nozzle, Venturi tube calculations |
| IEC 60534 | `control_valve` | Control valve Cv/Kv sizing |
| ASME BPVC | `geometry` | Tank head geometries (flanged & dished, ellipsoidal, hemispherical) |

---

## ChEDL Ecosystem Relationship

fluids is one component of Caleb Bell's ChEDL (Chemical Engineering Design Library):

| Library | Purpose | Relationship to fluids |
|---|---|---|
| **chemicals** | Pure-component property database (20,000+ compounds) | Provides fluid properties (density, viscosity, MW) used as inputs to fluids calculations |
| **thermo** | Thermodynamics and phase equilibria | Imports from fluids (dimensionless numbers); provides phase-dependent properties |
| **ht** | Heat transfer correlations | Pairs with fluids for combined thermal-hydraulic analysis |
| **fluids** | Fluid dynamics and piping design | Core hydraulics engine |

The libraries can be used independently but are designed to interoperate. For piping design workflows, fluids alone is sufficient when fluid properties are known; pairing with chemicals/thermo enables property-from-name lookups.

---

## API Design

- All functions accept **base SI units** (Pa, m, kg, K, s) — no unit system switching
- Functions are pure (no side effects, no global state)
- Consistent parameter naming: `Di` = inner diameter, `Do` = outer diameter, `Re` = Reynolds number, `eD` = relative roughness
- Return values are plain floats or tuples — no custom objects to learn
- Optional Numba JIT compilation via `fluids.numba` module for performance-critical loops

---

## Validation Approach

A test script was written at `tests/fluids_eval.py` covering:

1. **Friction factors** — Colebrook equation vs Moody chart reference values at Re=1e5 (eD=0.001), Re=1e6 (eD=0.0001), laminar (Re=1000), and transition (Re=4000)
2. **Fittings** — Crane TP-410 sharp entrance (K=0.5), normal exit (K=1.0), rounded bend
3. **Relief valves** — API 520 gas sizing (air, 1 MPa, 1 kg/s) and steam sizing (200C, 1.1 MPa)
4. **Compressible flow** — Isothermal gas flow through 100m pipe
5. **Pipe schedules** — `nearest_pipe()` for 100mm target diameter

**Note:** Python execution was blocked during this session. The test script is ready to run:
```
python3 tests/fluids_eval.py
```

The library's own test suite contains extensive validation against textbook and standards examples. The Crane TP-410 solved problems are reproduced in the documentation as worked examples.

---

## Integration Fit for digitalmodel

**Fit: very-high**

Immediate integration points for piping workflows:

1. **Pressure drop calculation** — `friction_factor()` + `fittings` K-factors for piping system hydraulics
2. **Pipe sizing** — `nearest_pipe()` for standard schedule selection
3. **Relief valve sizing** — API 520 compliance calculations for safety system design
4. **Compressible flow** — Gas pipeline sizing and pressure drop
5. **Control valve sizing** — IEC 60534 Cv/Kv calculations
6. **Flow metering** — Orifice plate sizing per ISO 5167

**Integration pattern:** fluids functions are pure and stateless — they can be called directly from digitalmodel calculation modules without wrapper classes. The SI-unit convention matches digitalmodel's existing approach.

---

## Strengths

- Zero compiled dependencies (pure Python, NumPy/SciPy optional)
- Comprehensive standards coverage (Crane, API, ASME, ISO, IEC)
- Well-documented with worked examples from Crane TP-410
- Active maintenance (v1.3.0 released Oct 2025, 1,789 commits)
- MIT license — no copyleft concerns
- Optional Numba acceleration for batch calculations
- Part of a coherent ecosystem (chemicals, thermo, ht)

## Limitations

- No built-in unit handling (user must ensure SI inputs)
- No pipe network solver (single-segment calculations only; network modeling requires iteration)
- No graphical output (Moody charts, system curves must be built externally)
- Two-phase flow models are correlation-based (not mechanistic)
- API 521 coverage is partial (fire-case sizing, not full flare system)

## Recommendation

**Adopt.** fluids should be the default piping hydraulics engine for digitalmodel workflows. Its pure-Python architecture, standards compliance, and clean API make it an ideal fit. Start with friction factor and pipe sizing modules, then expand to relief valve and control valve sizing as those workflows are built out.
