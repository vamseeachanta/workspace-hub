---
id: RES-003
type: resource
entry_type: reference
title: "BEMRosetta CLI supports mesh conversion only via -mesh mode"
category: tooling
domain:
  primary: hydrodynamics
  sub_domain: mesh-processing
tags: [bemrosetta, mesh, nemoh, cli, conversion]
repos: [digitalmodel]
confidence: 0.90
created: "2026-03-25"
last_validated: "2026-03-25"
source:
  name: "BEMRosetta GitHub Repository README"
  source_kind: codebase
  url: "https://github.com/BEMRosetta/BEMRosetta"
  retrieved: "2026-02-22"
provenance:
  method: manual
  reviewed_by: vamsee
  review_date: "2026-03-25"
related: [RES-001, RES-002]
ttl_days: 180
status: active
access_count: 0
file: ".claude/knowledge/entries/resources/RES-003-bemrosetta-mesh-mode-only.md"
---

# RES-003: BEMRosetta CLI supports mesh conversion only

## Reference
- **Executable**: `$BEMROSETTA_HOME/BEMRosetta_cl.exe`
- **CLI mode**: `-mesh` — converts between mesh formats (GDF, DAT, STL, etc.)
- **GUI mode**: Full BEM result viewer, comparison, and mesh editing
- **Nemoh**: The open-source BEM solver that BEMRosetta wraps for actual hydrodynamic computation

## Key Limitation
The CLI (`BEMRosetta_cl.exe`) only does mesh format conversion. It cannot run hydrodynamic analysis. For actual BEM computation, use Nemoh or Capytaine directly, then import results into BEMRosetta GUI for post-processing.
