---
name: drillbotics
description: SPE Drillbotics Mode V (virtual track) reference — competition requirements, module architecture, controller patterns, ROP models, D-WIS interoperability, and ACE Engineering capability mapping
version: 1.1.0
category: engineering/drilling
type: skill
trigger: manual
auto_execute: false
capabilities:
  - virtual_track_requirements
  - trajectory_planning
  - rop_modelling
  - wellbore_hydraulics
  - drilling_controller_design
  - well_control
  - formation_classification
  - dwis_interoperability
tools: [Read, Bash, Task]
related_skills: [drilling, production-engineering, oil-and-gas]
requires: []
see_also:
  - docs/strategy/drillbotics-engagement.md
  - docs/vision/VISION.md
---

# SPE Drillbotics — Mode V (Virtual Track) Skill

> Reference for the SPE Drillbotics virtual track competition. ACE Engineering's role
> is mentor / open-source contributor — the competition is students-only.
>
> Official: https://drillbotics.com | Guidelines: https://open-source-drilling-community.github.io/drillbotics-guidelines/latest/
> Open-source models: https://github.com/Open-Source-Drilling-Community

---

## Competition Overview

**Organiser**: SPE Drilling Systems Automation Technical Section (DSATS)
**Eligibility**: University student teams only (multi-disciplinary)
**ACE role**: Industry mentor, open-source contributor — not a competitor

**Mode V core challenge**: Build a Python-based (or equivalent) multi-module drilling
simulator that autonomously drills a 3D directional well to targets revealed only on
competition day, within a **3-hour window**. No pre-scripted trajectories allowed.

**Phases**:
- Phase I (Dec 31 deadline): Written design report covering architecture, models, validation
- Phase II (May/June): Live demonstration — targets revealed on the day; teams have 3 hours,
  multiple attempts; can debug and modify code during the window

---

## Required System Modules

### 1. Trajectory Planner

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

### 2. Trajectory Control Optimizer (TCO)

Closed-loop steering of the simulated bit along the planned path. Must correct for
BHA model uncertainty at each survey station. Reinforcement learning has been used
by winning teams (UiS 2021-2022) for generalization to unseen target geometries.

### 3. BHA Model (RSS and Motor)

**Critical constraint**: BHA type (Rotary Steerable System vs Adjustable Kick-Off motor)
is specified on competition day. Both must be pre-implemented and switchable.

Open-source references:
- `MADSim-Wilson-Simple-BHA-Model` (Open Source Drilling Community)
- `Aarsnes-and-Shor-Torsional-Model` (torsional vibration)

### 4. ROP Optimisation

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

### 5. Torque and Drag

Drillstring friction and axial/torque loads along the wellbore trajectory.
Used for WOB management and stuck-pipe detection.

Open-source reference: `Dixit-Drillstring-Model-2023` (Open Source Drilling Community)

**Status in ACE Engineering**: NOT YET IMPLEMENTED.

### 6. Wellbore Hydraulics / ECD

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

### 7. Well Control

Kick detection and automated shut-in. Scored as a separate category.

Detection signals:
- Flow-in/out differential > 5% sustained
- Pit volume gain > threshold
- Standpipe pressure anomaly

False-alarm rate is explicitly scored — conservative triggers that shut in unnecessarily
count against the team.

### 8. Formation Classification (ML)

Real-time identification of formation being drilled from surface drilling signals
(WOB, ROP, torque, vibration). Enables adaptive control parameter switching.

UMaT (2024 winner) used ensemble ML methods + a Python-based digital-twin architecture.

### 9. Operator HMI

Human-in-the-loop interface required since 2021. Criteria:
- Alarm management following alarm philosophy standards
- Levels-of-automation design (operator can always intervene)
- Mitigation of automation complacency ("ironies of automation")

### 10. D-WIS Interoperability (2025-2026 requirement)

All modules must expose data via Drilling Well Information Schema (D-WIS) semantic
network protocols. This is a mandatory gate for Phase II entry in the 2025-2026 cycle.

Reference: https://d-wis.org

---

## Scoring Summary

| Category | Notes |
|----------|-------|
| Trajectory accuracy | Distance from planned path to each target |
| Drilling efficiency | ROP achieved, time to TD |
| Dysfunction avoidance | Stick-slip, washout, lost circulation events |
| Well control | Kick detection speed, shut-in execution, false-alarm rate |
| HMI quality | Alarm management, automation levels design |
| Phase I report | Technical rigor of design document |
| Edge-AI bonus | +15 pts — optional offline small-model AI project |

---

## Open-Source Building Blocks

**Open Source Drilling Community** (https://github.com/Open-Source-Drilling-Community):

| Library | Purpose |
|---------|---------|
| `BitModelLibrary` | Bit-formation interaction models |
| `Dixit-Drillstring-Model-2023` | Drillstring mechanics |
| `Aarsnes-and-Shor-Torsional-Model` | Torsional vibration |
| `MADSim-Wilson-Simple-BHA-Model` | Simplified BHA model |
| `YPLCalibrationFromRheometer` | Mud rheology |

University of Stavanger's RSS simulator (Python) has been used as a baseline by multiple
competing teams and is available through the Open Source Drilling Community.

---

## ACE Engineering Gap vs Drillbotics Requirements

| Module | ACE Status | Priority to Build |
|--------|-----------|-----------------|
| Drilling domain knowledge | ✅ `drilling-expert` agent | — |
| Python sim infrastructure | ✅ `digitalmodel` | — |
| AI orchestration | ✅ workspace-hub | — |
| ROP model | ❌ Missing | **H1** (standalone client value) |
| Wellbore hydraulics | 🟡 Partial (CT-only) | **H1** — generalise `ct_hydraulics.py` |
| Torque and drag | ❌ Missing | **H2** |
| 3D trajectory planner | ❌ Missing | **H2** |
| Drilling controller | ❌ Missing | **H2** |
| Well control / kick detection | ❌ Missing | **H2** |
| Formation classification (ML) | ❌ Missing | **H2** |
| D-WIS semantic layer | ❌ Missing | **H3** |

Full engagement strategy: `docs/strategy/drillbotics-engagement.md`

---

## Published Papers (Mode V)

| Year | Paper | Venue |
|------|-------|-------|
| 2022 | Autonomous Directional Drilling Using RSS Simulator — Drillbotics 2020-2021 | IADC/SPE DC 2022 |
| 2023 | Autonomous Directional Drilling Simulator — Drillbotics 2021-2022 | IADC/SPE DC 2023 |
| 2024 | Directional Drilling with Scaled RSS and Virtual Well Control | IADC/SPE DC 2024 |
| 2025 | Dual Approach in Autonomous Directional Drilling — Drillbotics 1.5" and Virtual | IADC/SPE DC 2025 |

All available on OnePetro.
