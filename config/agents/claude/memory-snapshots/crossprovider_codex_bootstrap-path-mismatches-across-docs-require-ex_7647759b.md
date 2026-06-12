---
name: crossprovider codex bootstrap-path-mismatches-across-docs-require-ex
description: Bootstrap path mismatches across docs require explicit reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [portability, baseline, documentation]
---

When docs and scripts reference OpenFOAM (or similar tool) bootstrap paths that diverge (e.g., `/usr/lib/openfoam/` vs `/opt/openfoam/`), this creates portability ambiguity. The canonical baseline doc must freeze a single path after verifying it works on the target machine, not leave the contradiction unresolved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
