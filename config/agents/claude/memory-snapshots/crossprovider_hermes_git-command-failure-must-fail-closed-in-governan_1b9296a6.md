---
name: crossprovider hermes git-command-failure-must-fail-closed-in-governan
description: Git command failure must fail-closed in governance paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [error-handling, operations-governance, fail-closed]
---

Git operations returning non-zero exit codes should surface as blockers or warnings, not silently treated as 'clean' success. Operations governance and readiness paths require fail-closed semantics; silent pass-through hides infrastructure issues.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
