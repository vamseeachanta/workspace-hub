# SPE Drillbotics — ACE Engineering Engagement Strategy

> **WRK-375** | Created: 2026-02-24 | Status: Active
> Reference: https://jpt.spe.org/twa/spe-drillbotics-an-engineering-competition-and-gateway-to-leadership-development

---

## What Is Drillbotics

SPE Drillbotics is an annual applied R&D competition run by the **SPE Drilling Systems
Automation Technical Section (DSATS)**. Running since 2015. Two tracks:

- **Physical track (Mode P)** — build and operate a miniature 1.5" drilling rig
- **Virtual track (Mode V)** — build a full-physics drilling simulator with autonomous control

**Eligibility**: University student teams only (multi-disciplinary: petroleum, mechanical,
electrical, controls, CS). Industry professionals serve as judges and mentors — they do
not compete. ACE Engineering can engage as a **mentor or open-source contributor**, not
as a competitor.

### Mode V (Virtual Track) — What Teams Must Build

The virtual track deliverable is a Python-based (or equivalent) multi-module drilling
simulator that must autonomously drill a 3D directional well to targets **revealed only
on competition day**, within a 3-hour window. Key modules:

| Module | Description |
|--------|-------------|
| **Trajectory planner** | 3D path computation to multiple targets; cubic Bezier / minimum-curvature; DLS constraints |
| **Trajectory Control Optimizer (TCO)** | Closed-loop steering of simulated bit along planned path |
| **RSS / Motor BHA model** | Physics of bottom-hole assembly; must support both types (BHA type revealed on day) |
| **ROP optimisation** | Nonlinear constrained optimisation of WOB and RPM; formation-dependent |
| **Torque and drag** | Drillstring friction and axial/torque loads |
| **Wellbore hydraulics / ECD** | Managed pressure drilling, equivalent circulating density control |
| **Well control** | Kick detection (flow-in/out, pit level); automated shut-in; false-alarm rate scored |
| **Formation classification** | Real-time ML identification of rock type from drilling signals |
| **Operator HMI** | Human-in-the-loop interface; alarm management; levels-of-automation design |
| **D-WIS interoperability** | Semantic network layer per Drilling Well Information Schema (2025–2026 requirement) |

Scoring: trajectory accuracy, ROP/efficiency, dysfunction avoidance, well control performance,
HMI quality, Phase I design report, and optional Edge-AI bonus (+15 pts for offline small-model AI).

**Official resources:**
- https://drillbotics.com
- https://open-source-drilling-community.github.io/drillbotics-guidelines/latest/
- https://github.com/Open-Source-Drilling-Community (open-source building blocks)

---

## ACE Engineering Capability Gap Analysis

### Existing Capabilities (Covered)

| Drillbotics Requirement | ACE Capability | Location |
|------------------------|---------------|----------|
| Drilling domain knowledge | `drilling-expert` agent — well planning, optimisation, safety | `worldenergydata` |
| O&G production context | `oil-and-gas-expert` agent | `worldenergydata` |
| AI orchestration layer | Work queue + multi-agent framework | `workspace-hub` |
| Interactive reporting | Plotly dashboards, HTML reports | `digitalmodel`, `assethold` |
| Python simulation infrastructure | 704+ modules, pytest, uv | `digitalmodel` |

### Gaps (Not Yet Covered)

| Module | Gap | Standalone Value | Drillbotics Use |
|--------|-----|-----------------|----------------|
| **ROP model** | No Bourgoyne-Young or Warren ROP model | High — client projects | Virtual track core scoring metric |
| **Wellbore hydraulics** | No ECD, pressure-drop, annular velocity | High — client projects | Required for ECD control |
| **Torque and drag** | No soft/stiff-string T&D | High — client projects | Required for WOB/tension management |
| **3D trajectory planner** | No directional well planning | Medium — some client work | Core deliverable of Mode V |
| **Drilling controller** | No WOB/RPM closed-loop | Medium | Mode V autonomous control |
| **Well control module** | No kick detection / shut-in logic | Medium — safety critical | Scored separately |
| **Formation classification** | No ML formation identification | Medium | Real-time adaptive control |
| **D-WIS / semantic layer** | No DWIS-compliant data schema | Low currently | 2025-26 interoperability gate |

**Key insight**: The H1 gaps (ROP, hydraulics, T&D) have high standalone client value
independent of Drillbotics — they close real `digitalmodel` holes that affect every
well engineering project.

---

## Engagement Mode: (b) + (c) + Open-Source Contribution

ACE Engineering cannot compete directly (students-only). Selected approach:

### Mode (b) — Drillbotics Skill and Reference Guide

`/mnt/local-analysis/workspace-hub/.claude/skills/engineering/drilling/drillbotics/SKILL.md`
documents the virtual track requirements, technical modules, and ACE capability mapping.
Any team seeking mentorship or any ACE agent working on Drillbotics-adjacent problems
can use this as a reference.

### Mode (c) — Mentor / Industry Partner Positioning

ACE Engineering's engagement value proposition to competing teams:
- **Drilling domain expertise**: `drilling-expert` agent and O&G client project experience
  (ACMA, Saipem, Doris) provides real-world context for module validation
- **AI orchestration architecture**: The workspace-hub multi-agent framework is directly
  applicable to the multi-module Drillbotics system architecture (each module as an agent)
- **Open-source contribution**: H1 capability builds (ROP model, hydraulics) contributed
  to the Open Source Drilling Community GitHub are a natural fit and increase visibility

### Concrete Next Steps (H1 WRK candidates)

| Priority | Action | WRK | Benefit |
|----------|--------|-----|---------|
| H1 | ROP prediction model (Bourgoyne-Young + Warren) in `digitalmodel` | new WRK | Client projects + Drillbotics scoring |
| H1 | Wellbore hydraulics module (ECD, pressure drop, AV) | new WRK | Client projects + MPD control |
| H2 | Torque and drag model (soft-string) | new WRK | Trajectory optimisation |
| H2 | 3D directional trajectory planner | new WRK | Mode V core deliverable |
| H2 | Drilling controller prototype (PID → MPC) | new WRK | Autonomous drilling proof-of-concept |
| H3 | Full Mode V agent: sense → plan → act → report | new WRK | Level 4 autonomous workflow demo |

---

## Strategic Fit with VISION.md

Drillbotics Mode V is the **most concrete external benchmark** for the autonomous-production
vision (`docs/vision/VISION.md`). The Mode V system is exactly the Sense-Plan-Act loop
applied to drilling:

```
SENSE  → formation readings, WOB, RPM, torque, ECD, flow-in/out (simulator outputs)
PLAN   → trajectory controller + ROP optimiser compute next parameter set
ACT    → send WOB/RPM/flow commands; detect dysfunctions; escalate kicks to HMI
```

A working ACE Engineering Mode V capability (H2 milestone) would be the first fully
autonomous engineering workflow in the ecosystem — validated against externally-published
scoring criteria, not just internal acceptance tests.

---

*Last updated: 2026-02-24 | WRK-375 | workspace-hub/docs/strategy/*
