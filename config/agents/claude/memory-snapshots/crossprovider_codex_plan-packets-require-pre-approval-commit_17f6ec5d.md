---
name: crossprovider codex plan-packets-require-pre-approval-commit
description: Plan packets require pre-approval commit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [durability, approval-process, git-state]
---

Plans must be committed and pushed before approval is requested. Untracked plan files can diverge from approval state. If a plan is amended during review, re-read the amended version and verify against original findings before finalizing verdict. Transient specs break the audit trail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
