---
name: fe-analyst-bc-types-in-orcaflex
description: 'Sub-skill of fe-analyst: BC Types in OrcaFlex (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# BC Types in OrcaFlex (+2)

## BC Types in OrcaFlex


| BC Type | OrcaFlex Setting | Engineering Scenario |
|---|---|---|
| Fixed (clamped) | End A/B: Fixed | Flowline tie-in, rigid flange |
| Free | End A/B: Free | Anchor chain free end |
| Vessel-attached | End A/B: Connected to vessel | Riser top, mooring fairlead |
| Anchored (pinned) | End B: Fixed position, free rotation | Drag embedment anchor |
| Seabed contact | Seabed model active | Pipeline touchdown, mooring chain |
| Mid-line constraint | Constraint object | Clamp, bend stiffener tip |
| Coupled structure | Linked to another line | Pipeline-riser junction, in-line tee |


## BC Documentation Template


```
Boundary Conditions:
├── Top End (End A)
│   ├── Connection: Vessel "FPSO" / anchor point / fixed
│   ├── Position (x, y, z): [m, global]
│   ├── Degrees of freedom: Translational [fixed/free], Rotational [fixed/free]
│   └── Effective stiffness (if flexible connection): kx, ky, kz [kN/m]
│
├── Bottom End (End B)
│   ├── Connection: Seabed / anchor / fixed point
│   ├── Position (x, y, z): [m, global]
│   └── Chain/wire burial — effective anchor point
│
├── Seabed Model
│   ├── Type: Linear elastic / non-linear / PONDUS
│   ├── Normal stiffness: kn [kN/m/m]
│   ├── Friction coefficient: μ (axial and lateral)
│   └── Slope: θ_seabed [°]
│
└── Intermediate Constraints (if any)
    ├── Bend stiffener / bell mouth: position along line, stiffness curve
    ├── Clamps: position, gap, friction
    └── Buoyancy modules: start/end KP, spacing
```


## Common BC Mistakes to Flag


```python
bc_checks = {
    "anchor_drag_not_modelled": "End B fixed XYZ — ensure drag embedment verified separately",
    "vessel_motion_missing": "End A connected to vessel but no RAOs imported — static only",
    "seabed_stiffness_too_high": kn > 500,   # [kN/m/m] — causes numerical issues
    "friction_coeff_zero": mu_axial == 0.0,  # Under-conservative for walking
    "free_end_tension_check": end_tension < 0,  # Negative = compression — flag
}
```

---
