---
name: crossprovider codex acceptance-criteria-should-not-permit-or-no-lift
description: Acceptance criteria should not permit 'or no-lift' escape hatches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, closure-risk, approval-gate]
---

Criteria like 'above 8/21 runnable coverage, OR explicitly approved no-lift source gap' create approval-without-closure risk when source evidence exists (e.g., RSU-0077 with documented cases). The OR allows approval despite an unresolved gap. Close the gap explicitly or document why it cannot be closed; do not use OR to bypass the completion threshold.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
