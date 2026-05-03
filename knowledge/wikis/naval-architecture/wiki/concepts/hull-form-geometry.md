---
title: "Hull-Form Geometry"
tags: ["hull-form", "lines-plan", "sectional-area-curve", "coefficients", "geometry"]
sources:
  - naval-architecture-resources
added: 2026-05-02
last_updated: 2026-05-02
see_also:
  - concepts/hydrostatics.md
  - concepts/ship-design.md
---

# Hull-Form Geometry

## Scope

This page defines the geometric description of a ship's hull — lines plan, sectional-area curve, body plan, and the form coefficients derived from them. It is the geometric companion to `concepts/hydrostatics.md` (which covers buoyancy properties at a given waterline) and to `concepts/ship-design.md` (which covers the design-spiral process). It is NOT a stability page (see `concepts/stability.md`) and NOT a structural page (see `concepts/ship-structures.md`).

## Key Concepts

- **Lines plan (lines drawing)** — orthographic projection of the hull surface in three views: profile (sheer plan), half-breadth (waterlines), and body plan (transverse sections).
- **Body plan** — transverse sections at fixed station spacing; forward sections drawn on the right of centerline, aft on the left.
- **Sectional-area curve (SAC)** — submerged cross-sectional area plotted against length; integrates to displaced volume.
- **Stations and bow/stern profiles** — typical 11- or 21-station division of length-between-perpendiculars (LBP).
- **Form coefficients (dimensionless)** — block (Cb), midship (Cm), prismatic (Cp), waterplane (Cwp), vertical prismatic (Cvp); see `concepts/hydrostatics.md` for definitions.
- **Length, beam, draft definitions** — LOA, LBP, LWL, B, T, D; choice of length for coefficient computation matters.
- **Parametric hull-form generation** — Lackenby shift, Holtrop input parameterization, NURBS surface modeling.
- **Hull-form fairness** — geometric continuity (G1/G2) across stations; checked visually and via curvature plots.

## Standards / References

- SNAME — *Principles of Naval Architecture*, Volume I (Second Revision), hull-form description chapter. Local: `/mnt/ace/docs/_standards/SNAME/textbooks/Principles-of-Naval-Architecture-SecondRevision-Vol1.pdf`.
- Tupper — *Introduction to Naval Architecture* (5e), ship-form calculations chapter (https://shop.elsevier.com/books/introduction-to-naval-architecture/tupper/978-0-08-098237-3).
- ITTC — Recommended Procedures, geometry-related submission requirements (https://ittc.info/).

## Cross-References

- [Ship Hydrostatics](hydrostatics.md) — coefficients and waterline-dependent properties.
- [Ship Design Process](ship-design.md) — how lines-plan iteration sits in the design spiral.
