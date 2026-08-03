---
name: crossprovider codex scope-creep-silently-adds-adjacent-measures-past
description: Scope creep silently adds adjacent measures past acceptance gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [scope, spec, acceptance-criteria, spec-compliance]
---

When a PR explicitly scopes out intensity measures but the implementation computes and emits related measures (e.g., PGV/PGD alongside PGA), those measures become durable parts of the report contract. Scope gates must be explicit in acceptance criteria and tests must enforce them to catch adjacent-measure creep early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
