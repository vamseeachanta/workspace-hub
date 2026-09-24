---
name: crossprovider codex skip-and-error-reasons-must-encode-root-cause-fo
description: Skip and error reasons must encode root cause for downstream triage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [harness, error-handling, observability, status-semantics]
---

When a repo can be skipped for multiple independent reasons (absent-file vs untracked vs tool-failure vs format-incompatible), use specific reason codes for each. Downstream triage and retry decisions depend on knowing WHY a repo was skipped, not just that it was.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
