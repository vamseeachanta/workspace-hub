---
name: crossprovider codex gmshtofoam-assigns-generic-patch-type-to-all-bou
description: gmshToFoam assigns generic patch type to all boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [mesh-conversion, cfd, boundary-semantics]
---

Gmsh-to-OpenFOAM conversion (`gmshToFoam`) assigns every imported boundary the generic `patch` type, regardless of physical intent (wall, symmetry, etc.). Solver boundary conditions may fail or apply incorrectly. Validation must check actual patch types post-conversion and normalize or reject non-matching types.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
