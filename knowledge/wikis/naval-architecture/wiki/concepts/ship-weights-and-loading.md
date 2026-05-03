---
title: "Ship Weights and Loading"
tags: ["weights", "loading", "deadweight", "lightship", "load-line"]
sources:
  - naval-architecture-resources
added: 2026-05-02
last_updated: 2026-05-02
see_also:
  - concepts/hydrostatics.md
  - concepts/ship-structural-strength.md
---

# Ship Weights and Loading

## Scope

This page defines the weight-and-loading bookkeeping used in ship design and operation: lightship vs deadweight breakdown, longitudinal weight distribution, and the loading-condition framework that feeds stability and strength checks. It is the load-side input for `concepts/ship-structural-strength.md` and complements `concepts/hydrostatics.md` (which evaluates the floating equilibrium for a given weight set).

## Key Concepts

- **Lightship weight** — fully outfitted ship with no cargo, fuel, stores, ballast, or crew effects; sum of structure, machinery, outfit, and margin.
- **Deadweight (DWT)** — total carried weight at a specified draft: cargo, fuel, lubricants, fresh water, ballast, stores, crew and effects.
- **Displacement** — lightship + deadweight = displaced water mass at the operating draft.
- **Weight groups** — SWBS (Ship Work Breakdown Structure, US Navy) or ESWBS classification of weight items by function.
- **Centers of gravity (LCG, VCG, TCG)** — longitudinal, vertical, and transverse aggregated weight centers.
- **Loading conditions** — standard sets (departure full load, arrival full load, departure ballast, arrival ballast, partial loads) evaluated for stability and strength.
- **Load line (Plimsoll mark)** — regulatory minimum-freeboard mark indicating maximum allowable draft by sea zone and season.
- **Longitudinal weight distribution** — weight per unit length along the hull; subtracted from the buoyancy distribution to give the load curve.
- **Load-shear-bending integration** — twice-integrated load curve gives shear and bending-moment distributions.
- **Trim and heel** — equilibrium pose adjustments needed to balance moments from the LCG/LCB offset.
- **Weight margin** — design allowance for weight growth during construction and over the ship's life.

## Standards / References

- IMO — *International Convention on Load Lines* (Maritime Safety landing: https://www.imo.org/en/OurWork/Safety/Pages/Default.aspx).
- IACS — load-line and freeboard implementation requirements published by member societies.
- SNAME — *Principles of Naval Architecture*, Volume I (Second Revision), weight-estimation appendix.

## Cross-References

- [Ship Hydrostatics](hydrostatics.md) — equilibrium and trim mechanics consuming the weight distribution.
- [Ship Structural Strength](ship-structural-strength.md) — load curve as input to bending-moment evaluation.
