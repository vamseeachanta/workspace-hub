---
title: "Riser-Soil Interaction"
tags: [riser, soil, touchdown, trench, p-y, scr]
added: 2026-05-02
last_updated: 2026-05-02
---

# Riser-Soil Interaction

## Scope

This page covers the soil-stiffness models and trench-evolution physics that drive boundary response at the SCR touchdown zone. It is NOT a VIV page — see [[viv-riser-fatigue]]. It is NOT an SCR design-state page — see [[riser-steel-catenary-design]] for hang-off and TDP migration physics.

## Key Concepts

- **Touchdown zone (TDZ)** — segment of the riser making intermittent contact with the seabed; stress concentration migrates with vessel offset and tide.
- **Vertical soil stiffness** — first-loading, unloading, and re-loading branches; cyclic degradation under repeated contact.
- **Linear elastic soil model** — single vertical spring per node; quick screening, non-conservative for fatigue at the TDZ.
- **Non-linear hyperbolic soil model** — secant stiffness reduces with displacement; closer to measured pipe-soil response.
- **Aubeny-Biscontin model** — non-linear cyclic soil stiffness specifically calibrated for catenary-riser TDZ behaviour.
- **Trench-formation physics** — repeated TDZ cycling remoulds the soft sediment, forming a trench over weeks to years; trench geometry alters local boundary stiffness and stress hot-spot location.
- **Trench-effect on fatigue** — shallow trench can reduce TDZ stress range; deep trench can reintroduce a sharper stress concentration at the trench shoulder.
- **Suction during uplift** — sticky clay generates suction during pipe uplift; modelled as a separate branch in the soil-spring constitutive.
- **Lateral soil resistance** — relevant for lateral TDZ excursion under cross-current; analogous to pipeline lateral-buckling soil response.

## Standards / References

- DNV-OS-F201 (Dynamic Risers) — provides the design framework that consumes soil-stiffness inputs: [DNV-OS-F201](../../../engineering-standards/wiki/standards/dnv-os-f201.md).
- API STD 2RD (Dynamic Risers for Floating Production Systems): [API STD 2RD](../../../engineering-standards/wiki/standards/api-std-2rd.md).

## Cross-References

- [[riser-steel-catenary-design]] — SCR design state consuming the soil-stiffness model.
- [[viv-riser-fatigue]] — VIV-fatigue mechanics at the TDZ where soil-stiffness sets the boundary.
- [[pile-capacity-alpha-method]] — adjacent soil-shear correlation framework used for foundation design.
- [[riser-global-analysis-load-cases]] — accidental and serviceability cases that depend on TDZ stiffness.
