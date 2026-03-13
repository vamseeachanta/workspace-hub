# Drilling Engineering Study
> WRK-5059 Feature Spec

## Scope

Model core drilling engineering calculations: torque and drag, hydraulics, well control, casing design, and drill string mechanics — for fast-running Python assessment tools.

## Key Parameters

| Symbol | Description | Units |
|--------|-------------|-------|
| WOB | Weight on bit | kN |
| RPM | Rotary speed | rev/min |
| Q | Flow rate | m³/s |
| ECD | Equivalent circulating density | kg/m³ |
| MW | Mud weight | kg/m³ |
| SICP/SIDPP | Shut-in casing/drill pipe pressure | kPa |
| mu | Friction factor (T&D) | — |
| sigma_y | Yield strength (casing) | MPa |

## Sub-domains

1. **Torque and drag** — soft-string, stiff-string models, buckling onset
2. **Drilling hydraulics** — ECD, pressure loss, bit hydraulics optimisation
3. **Well control** — kick tolerance, kill sheet, volumetric methods
4. **Casing design** — burst/collapse/tension, biaxial/triaxial, connection rating
5. **Drill string mechanics** — critical RPM, lateral vibration, WOB transfer

## Child WRKs

| WRK | Title | Status |
|-----|-------|--------|
| TBD | Literature gathering | pending |
| TBD | Method assessment & selection | pending |
| TBD | Python implementation | pending |

## Output Deliverables

- `digitalmodel/docs/domains/drilling/drilling-engineering-literature.md`
- `digitalmodel/docs/domains/drilling/drilling-engineering-method-selection.md`
- `digitalmodel/src/digitalmodel/drilling/` (new namespace)
