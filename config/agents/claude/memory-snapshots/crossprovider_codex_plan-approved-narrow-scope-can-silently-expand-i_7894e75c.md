---
name: crossprovider codex plan-approved-narrow-scope-can-silently-expand-i
description: Plan-approved narrow scope can silently expand in code without registry gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, plan-review, validation-gap, scope-creep]
---

Multiple llm-wiki implementations (issue #80 CLI, issue #290 export workflow) have shipped optional/future features as normal commands without machine-readable availability matrices. Validators and tests only check that features work, not that they respect the approved scope. Fix: require explicit registry (query_sources.json, availability_matrix.json) checked by validators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
