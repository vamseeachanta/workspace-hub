# Propeller-Rudder Interaction Study
> WRK-1147 Feature Spec

## Scope

Model the hydrodynamic interaction between a ship's propeller and rudder across the full engine operating envelope: engine-off (locked/free-wheeling propeller) through RPM-driven drive-off to rated speed.

## Key Parameters

| Symbol | Description | Units |
|--------|-------------|-------|
| n | Propeller shaft speed | rev/s (RPS) |
| D | Propeller diameter | m |
| V | Ship speed (advance speed) | m/s |
| J = V/(n·D) | Advance ratio | — |
| KT | Thrust coefficient | — |
| KQ | Torque coefficient | — |
| P | Delivered shaft power | kW |
| AR | Rudder area | m² |
| Va | Axial slipstream velocity at rudder | m/s |
| Vt | Tangential slipstream velocity at rudder | m/s |

## Operating Regimes

1. **Engine-off, locked** — n = 0; J → ∞; propeller drag, wake deficit at rudder
2. **Engine-off, free-wheeling** — n = n_fw (windmilling equilibrium); small wake
3. **Startup / low RPM** — n low, J high; propeller lightly loaded; slipstream developing
4. **Drive-off** — n ramps 0 → n_rated; J decreases; thrust, torque, slipstream grow
5. **Full ahead** — n = n_rated, design J; maximum propeller-rudder interaction

## Child WRKs

| WRK | Title | Status |
|-----|-------|--------|
| WRK-1148 | Literature gathering | pending |
| WRK-1149 | Method assessment & selection | pending (blocked by WRK-1148) |
| WRK-1150 | Python implementation with RPM sweep | pending (blocked by WRK-1149) |

## Output Deliverables

- `docs/hydrodynamics/propeller-rudder-literature.md`
- `docs/hydrodynamics/propeller-rudder-method-selection.md`
- `digitalmodel/src/digitalmodel/hydrodynamics/propeller_rudder/`
- `examples/propeller_rudder_driveoff.py`
