---
title: "Damage Stability"
tags: ["damage-stability", "subdivision", "solas", "probabilistic", "attained-index"]
sources:
  - naval-architecture-resources
added: 2026-05-02
last_updated: 2026-05-02
see_also:
  - concepts/stability.md
  - concepts/intact-stability-criteria.md
---

# Damage Stability

## Scope

This page covers ship stability after compartment flooding — the regulatory framework, methods, and key concepts used to evaluate post-damage survivability. It is the flooded-condition counterpart to `concepts/intact-stability-criteria.md` and refers back to the GZ-curve mechanics on `concepts/stability.md`. It does NOT duplicate intact-criteria thresholds and does NOT cover collision energy (a structures topic).

## Key Concepts

- **Subdivision** — division of the hull by watertight bulkheads to limit floodable volume after damage.
- **Lost-buoyancy method** — flooded compartment treated as outside the hull boundary; remaining buoyancy carries the ship.
- **Added-weight method** — floodwater treated as cargo; alternative bookkeeping yielding the same equilibrium.
- **Floodable length curve** — maximum length of any compartment that can flood without immersing the margin line.
- **Probabilistic damage stability** — attained subdivision index (A) compared to required (R); index combines probability of damage location, extent, and survivability of each scenario.
- **Deterministic damage stability** — prescribed damage cases (one- or two-compartment standards) tested against survival criteria.
- **Stages of flooding** — intermediate, equilibrium, and final flooded conditions; cross-flooding arrangements considered.
- **Permeability** — fraction of compartment volume available for water (machinery, accommodation, cargo, void differ).
- **Margin line** — geometric reference 76 mm below the bulkhead deck at side; used in deterministic checks.

## Standards / References

- IMO — *SOLAS Chapter II-1* subdivision and damage-stability regulations (Maritime Safety landing: https://www.imo.org/en/OurWork/Safety/Pages/Default.aspx).
- IMO — *MSC.281(85)* explanatory notes on probabilistic damage stability (named only; clauses reside in the future `wiki/standards/imo-solas-ii-1.md`).
- SNAME — *Principles of Naval Architecture*, Volume I (Second Revision), damage-stability chapter.

## Cross-References

- [Ship Stability](stability.md) — GZ-curve mechanics referenced by post-damage equilibrium analysis.
- [Intact Stability Criteria](intact-stability-criteria.md) — companion criteria for the upright condition.
