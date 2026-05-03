---
title: "Steel Catenary Riser (SCR) — Design State"
tags: [riser, scr, catenary, design, touchdown]
added: 2026-05-02
last_updated: 2026-05-02
---

# Steel Catenary Riser (SCR) — Design State

## Scope

This page covers the design-state physics of a Steel Catenary Riser (SCR): hang-off geometry, touchdown-point migration under vessel offset, departure-angle envelope, and the soil-trench effect on stress hot spots. It is NOT a VIV-fatigue page — that scope lives on [[viv-riser-fatigue]] (S-N curves, DFF, wake interference, rainflow counting). It is NOT a soil-stiffness modelling page — that lives on [[riser-soil-interaction]].

## Key Concepts

- **Hang-off configuration** — flex-joint, stress joint, or pull-tube; sets the angular boundary condition at the vessel.
- **Departure angle envelope** — the range of hang-off angles spanned across vessel near/far/cross offsets governs the upper-curvature hot spot.
- **Touchdown point (TDP)** — where the riser first contacts the seabed; a stress concentration that migrates under vessel offset and tide.
- **TDP migration window** — fore-aft TDP travel scales with water-depth-to-offset ratio; relevant for selecting wall-thickness step locations.
- **Soil-trench effect** — repeated TDP cycling forms a trench that alters the local boundary stiffness; trenches deepen over months to years.
- **Wall-thickness profile** — typically thicker at hang-off and TDP for fatigue allowance; the joint stack must align with stress hot spots.
- **Hang-off load components** — top tension, vessel offset moment, and dynamic amplification from heave and pitch.

## Standards / References

- DNV-OS-F201 (Dynamic Risers) — limit-state design of metallic dynamic risers: [DNV-OS-F201](../../../engineering-standards/wiki/standards/dnv-os-f201.md).
- API STD 2RD (Dynamic Risers for Floating Production Systems): [API STD 2RD](../../../engineering-standards/wiki/standards/api-std-2rd.md).

## Cross-References

- [[viv-riser-fatigue]] — VIV-fatigue mechanics for the SCR girth welds at TDP and hang-off.
- [[riser-soil-interaction]] — soil-stiffness models that drive TDP boundary response.
- [[riser-global-analysis-load-cases]] — extreme, accidental, and serviceability load cases applied to the SCR.
- [[riser-configurations]] — topology context for the free-hanging catenary archetype.
- [[fea-structural-analysis]] — local stress analysis at the hang-off connector and TDP weld.
