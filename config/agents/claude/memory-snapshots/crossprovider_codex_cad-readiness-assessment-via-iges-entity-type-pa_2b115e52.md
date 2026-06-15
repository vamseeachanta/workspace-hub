---
name: crossprovider codex cad-readiness-assessment-via-iges-entity-type-pa
description: CAD readiness assessment via IGES entity type parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cfd, geometry-validation, iges]
---

To determine CFD geometry readiness, parse IGES files for entity types: NURBS surface entities indicate aero-ready geometry, lines/arcs/annotations indicate component CAD. Empirical aero data (e.g., downforce spreadsheets) is separate from CFD geometry readiness, so assess each dimension independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
