---
name: crossprovider codex t2-plans-must-specify-data-flow-mechanics-and-fa
description: T2 plans must specify data-flow mechanics and fail-closed behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, t2-scope, data-architecture, recurring-blocker]
---

T2 multi-file plans fail review when they name inputs but omit join paths, fail-closed behavior for missing data, column provenance, or field mapping. Issue #702 iterations showed this as recurring MAJOR blocker across multiple review rounds; plans must document how missing/absent inputs are handled.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
