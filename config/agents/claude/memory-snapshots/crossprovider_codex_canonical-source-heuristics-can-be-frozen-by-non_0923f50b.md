---
name: crossprovider codex canonical-source-heuristics-can-be-frozen-by-non
description: Canonical-source heuristics can be frozen by non-overwrite policies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [technical-debt-hazard, canonical-source-authority, governance]
---

Existing O&G code uses `sorted(labels)[0]` as a heuristic default for canonical roots. Non-overwrite policies preserve these implicit heuristics as if they were human decisions, creating silent policy drift. Heuristic vs policy-decided distinctions must be explicit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
