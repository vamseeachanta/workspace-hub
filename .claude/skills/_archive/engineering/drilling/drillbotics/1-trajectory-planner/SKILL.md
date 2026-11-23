---
name: drillbotics-1-trajectory-planner
description: 'Sub-skill of drillbotics: 1. Trajectory Planner (+9).'
version: 1.1.0
category: engineering/drilling
type: reference
scripts_exempt: true
---

# 1. Trajectory Planner (+9)

## 1. Trajectory Planner


3D directional well-path computation from surface to multiple downhole targets.
Algorithms used by winning teams: cubic Bezier curves, minimum-curvature method.
Constraints: dogleg severity (DLS) limits, survey station uncertainty propagation.

```python
# Key inputs
targets: list[Point3D]     # revealed on competition day
dls_max: float             # deg/100ft — formation / BHA constraint
survey_uncertainty: float  # typical ±0.5° inclination, ±1° azimuth

# Key outputs
planned_path: list[SurveyStation]   # MD, inclination, azimuth at each station
```


## 2. Trajectory Control Optimizer (TCO)


Closed-loop steering of the simulated bit along the planned path. Must correct for
BHA model uncertainty at each survey station. Reinforcement learning has been used
by winning teams (UiS 2021-2022) for generalization to unseen target geometries.


## 3. BHA Model (RSS and Motor)


**Critical constraint**: BHA type (Rotary Steerable System vs Adjustable Kick-Off motor)
is specified on competition day. Both must be pre-implemented and switchable.

Open-source references:
- `MADSim-Wilson-Simple-BHA-Model` (Open Source Drilling Community)
- `Aarsnes-and-Shor-Torsional-Model` (torsional vibration)


## 4. ROP Optimisation


Real-time, formation-dependent optimisation of WOB and RPM to maximise ROP without
causing dysfunctions. Typically a nonlinear constrained optimisation problem.

**Bourgoyne-Young model** (eight-parameter, industry standard):
```
ROP = f(WOB, RPM, d_bit, ECD, formation_coefficients, bit_wear, overbalance, compaction)
```

**Warren model** (simplified, two-parameter):
```
ROP = K * (WOB / d_bit)^a * RPM^b
```

**Status in ACE Engineering**: NOT YET IMPLEMENTED. Gap identified in WRK-375.
Candidate location: `digitalmodel/well/drilling/rop_model.py`


## 5. Torque and Drag


Drillstring friction and axial/torque loads along the wellbore trajectory.
Used for WOB management and stuck-pipe detection.

Open-source reference: `Dixit-Drillstring-Model-2023` (Open Source Drilling Community)

**Status in ACE Engineering**: NOT YET IMPLEMENTED.


## 6. Wellbore Hydraulics / ECD


Managed pressure drilling: keep bottomhole pressure inside the mud-weight window.

| Parameter | Formula | Purpose |
|-----------|---------|---------|
| ECD | `MW + (annular_ΔP / (0.052 × TVD))` | Formation overbalance control |
| Annular velocity | `Q / (d_hole² − d_pipe²) × 0.408` | Cuttings transport |
| Pump pressure | Fanning friction + acceleration components | Surface pump management |

**Status in ACE Engineering**: PARTIAL — CT hydraulics exists at
`digitalmodel/src/digitalmodel/marine_ops/ct_hydraulics/ct_hydraulics.py`
(ECD, pressure drop, Reynolds/friction, pump pressure). Needs generalisation to
arbitrary pipe/annulus diameters and multi-phase flow. Gap: ~250 lines to extend.


## 7. Well Control


Kick detection and automated shut-in. Scored as a separate category.

Detection signals:
- Flow-in/out differential > 5% sustained
- Pit volume gain > threshold
- Standpipe pressure anomaly

False-alarm rate is explicitly scored — conservative triggers that shut in unnecessarily
count against the team.


## 8. Formation Classification (ML)


Real-time identification of formation being drilled from surface drilling signals
(WOB, ROP, torque, vibration). Enables adaptive control parameter switching.

UMaT (2024 winner) used ensemble ML methods + a Python-based digital-twin architecture.


## 9. Operator HMI


Human-in-the-loop interface required since 2021. Criteria:
- Alarm management following alarm philosophy standards
- Levels-of-automation design (operator can always intervene)
- Mitigation of automation complacency ("ironies of automation")


## 10. D-WIS Interoperability (2025-2026 requirement)


All modules must expose data via Drilling Well Information Schema (D-WIS) semantic
network protocols. This is a mandatory gate for Phase II entry in the 2025-2026 cycle.

Reference: https://d-wis.org

---
