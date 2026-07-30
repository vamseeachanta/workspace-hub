---
name: crossprovider codex licensed-solver-work-must-route-through-licensed
description: Licensed solver work must route through licensed hosts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [platform-constraint, architecture, licensing, solver-access]
---

OrcFxAPI and licensed solver execution are available only on licensed Windows workstations. Deterministic input bundles (JSON manifests) route to the licensed host, results return for verification and publication. This architecture preserves licensing compliance and avoids executing on unlicensed Linux infrastructure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
