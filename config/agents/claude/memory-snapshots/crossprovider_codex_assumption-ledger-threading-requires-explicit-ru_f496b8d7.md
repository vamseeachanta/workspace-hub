---
name: crossprovider codex assumption-ledger-threading-requires-explicit-ru
description: Assumption ledger threading requires explicit runner APIs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [architecture, threading, provenance, api-design]
---

Runners (orcawave, aqwa) do not inherit ledger from resolver; must add optional `assumption_ledger` parameters to `run()`/`prepare()` and attach to result, or provenance is silently lost before report generation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
