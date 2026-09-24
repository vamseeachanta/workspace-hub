---
name: crossprovider gemini gate-validation-implement-evidence-predicate-onc
description: Gate validation: implement evidence predicate once as canonical source of truth
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-gates, dry-principle, harness-design]
---

Gate-checking logic (required artifacts, field validation, staleness rules) must be a single executable checker called by all entrypoints (shell scripts, Python validators, runtime orchestrators), not re-implemented per caller. Re-implementation spreads rule logic and enables silent drift.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
