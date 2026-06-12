---
name: crossprovider hermes incomplete-unattended-terminal-runs-need-explici
description: Incomplete unattended terminal runs need explicit startup checklists and fallback paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, error-handling, unattended-runs]
---

When relaunching incomplete parallel terminals, require an explicit 3-item startup checklist (issue read, files inspected, first step) printed before execution. For permission-constrained runs, provide an explicit read-only fallback mode (analysis + patch guidance) instead of silently failing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
