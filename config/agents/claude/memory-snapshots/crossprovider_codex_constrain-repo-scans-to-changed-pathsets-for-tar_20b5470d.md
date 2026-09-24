---
name: crossprovider codex constrain-repo-scans-to-changed-pathsets-for-tar
description: Constrain repo scans to changed pathsets for targeted reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, efficiency, scoping]
---

Broad repo scans (legal, safety, secrets) are noisy for issue-specific reviews. Use pathset filtering or --diff-only flags to scan only changed files; this keeps findings scoped to the issue and avoids baseline violations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
