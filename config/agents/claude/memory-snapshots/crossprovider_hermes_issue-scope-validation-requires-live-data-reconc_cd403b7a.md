---
name: crossprovider hermes issue-scope-validation-requires-live-data-reconc
description: Issue scope validation requires live data reconciliation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, validation, execution-gating]
---

Before executing a plan, reconcile the issue's stated scope against actual system state (e.g., compare stated collections against which ones have phase-A outputs). Mismatches block execution cleanly. (#2369 discovered issue named ISOPE as ready but ISOPE lacked phase-A summaries.)

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
