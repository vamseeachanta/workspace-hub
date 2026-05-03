---
title: "Propeller Theory"
tags: ["propeller", "open-water", "kt", "kq", "advance-coefficient", "blade-element"]
sources:
  - naval-architecture-resources
added: 2026-05-02
last_updated: 2026-05-02
see_also:
  - concepts/resistance-propulsion.md
  - concepts/marine-propulsors.md
---

# Propeller Theory

## Scope

This page summarizes the theoretical frameworks used to characterize an isolated marine propeller and its interaction with the hull. It is the analytical companion to `concepts/marine-propulsors.md` (which surveys propulsor types) and feeds into `concepts/resistance-propulsion.md` (the parent router page). It does NOT enumerate cavitation thresholds, classification-society blade-thickness rules, or noise-prediction methods.

## Key Concepts

- **Momentum (actuator-disc) theory** — propeller idealized as an infinitely thin disc imparting axial momentum; yields the ideal-efficiency upper bound.
- **Blade-element theory** — propeller blade discretized into radial elements treated as 2-D airfoils; integrates section lift/drag along the blade.
- **Lifting-line and lifting-surface theory** — vortex-based formulations that account for span-wise circulation and induced velocities.
- **Open-water characteristics** — KT (thrust coefficient), KQ (torque coefficient), and eta_0 (open-water efficiency) plotted against J (advance coefficient).
- **Advance coefficient (J = Va / (n*D))** — non-dimensional inflow speed; defines operating point on the open-water curves.
- **Wake fraction (w)** — reduction in inflow velocity behind the hull relative to ship speed; gives effective advance velocity Va = V(1-w).
- **Thrust deduction (t)** — reduction in net thrust delivered to the hull due to local pressure changes; gives effective thrust T(1-t).
- **Hull efficiency (eta_H = (1-t)/(1-w))** — propulsive coefficient component capturing hull-propeller interaction.
- **Relative-rotative efficiency (eta_R)** — ratio of in-behind to open-water torque at the same thrust.
- **Cavitation** — vapor formation when local pressure drops to vapor pressure; characterized by cavitation number sigma.

## Standards / References

- ITTC — Recommended Procedures for propeller open-water test and analysis (https://ittc.info/).
- SNAME — *Principles of Naval Architecture*, Volume II — *Resistance, Propulsion and Vibration*, propeller chapters.
- Bertram — *Practical Ship Hydrodynamics*, propeller-theory chapter.

## Cross-References

- [Marine Propulsors](marine-propulsors.md) — propulsor-type catalogue and selection drivers.
- [Ship Resistance and Propulsion](resistance-propulsion.md) — parent router page.
