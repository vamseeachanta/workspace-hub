# Drilling Riser Engineering Study
> WRK-5058 Feature Spec

## Scope

Model drilling riser analysis across key engineering disciplines: stackup/tension, operability envelopes, VIV fatigue, structural damping, and tool passage — for fast-running Python assessment tools.

## Key Parameters

| Symbol | Description | Units |
|--------|-------------|-------|
| WD | Water depth | m |
| T_top | Top tension | kN |
| T_eff | Effective tension (incl. buoyancy) | kN |
| Hs | Significant wave height | m |
| Vc | Current velocity profile | m/s |
| f_n | Natural frequency (nth mode) | Hz |
| D_fat | Fatigue damage (Miner's sum) | — |
| OD/ID | Riser outer/inner diameter | m |
| EI | Bending stiffness | N·m² |

## Sub-domains

1. **Stackup & tension** — joint count, buoyancy, top tension vs water depth
2. **Operability** — vessel offset limits, disconnect criteria, heading sensitivity
3. **VIV & fatigue** — mode shapes, response amplitude, fatigue damage
4. **Structural damping** — parametric influence on dynamic amplification
5. **Tool passage** — BHA/completion tool clearance through riser bore

## Child WRKs

| WRK | Title | Status |
|-----|-------|--------|
| TBD | Literature gathering | pending |
| TBD | Method assessment & selection | pending |
| TBD | Python implementation | pending |

## Output Deliverables

- `digitalmodel/docs/domains/drilling/drilling-riser-literature.md`
- `digitalmodel/docs/domains/drilling/drilling-riser-method-selection.md`
- `digitalmodel/src/digitalmodel/drilling_riser/` (extended)
