---
name: crossprovider codex approval-eligibility-requires-local-filesystem-v
description: Approval eligibility requires local filesystem verification beyond GitHub evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-workflow, implementation-eligibility, verification-strategy]
---

Implementation requires both live GitHub status:plan-approved label AND verified local .planning/plan-approved/<issue>.md marker file presence. GitHub search provides committed marker state and live issue labels but cannot prove local uncommitted filesystem state. When local inspection is blocked or unavailable, eligibility cannot be granted even if GitHub evidence appears complete; mark such findings evidence-only and incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
