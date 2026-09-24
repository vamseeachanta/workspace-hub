---
name: crossprovider codex swallowed-failures-on-diagnostic-gate-scripts-ar
description: Swallowed failures on diagnostic/gate scripts are more dangerous than loud failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-idioms, error-handling, gates, fail-open]
---

Constructs like `|| true`, `|| :`, and `2>/dev/null` on validation/checking/legal-gate scripts hide false negatives (the check never ran but success is reported). A loud failure that crashes is a bug; a silent failure that passes is a lie. Reserve swallowing for scripts where missing a step is acceptable; diagnostic gates must fail visibly when the check cannot run.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
