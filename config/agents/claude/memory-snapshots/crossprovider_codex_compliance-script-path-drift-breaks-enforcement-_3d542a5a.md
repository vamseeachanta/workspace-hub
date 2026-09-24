---
name: crossprovider codex compliance-script-path-drift-breaks-enforcement-
description: Compliance script path drift breaks enforcement silently
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, maintenance-hazard, verification]
---

Repo structure changes cause compliance scripts to reference outdated paths, silently breaking enforcement. Updated paths require verification via syntax checks (bash -n) and smoke-run on pilot repos before trusting enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
