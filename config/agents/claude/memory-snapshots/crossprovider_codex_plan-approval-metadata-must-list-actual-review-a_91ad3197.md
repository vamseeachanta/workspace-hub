---
name: crossprovider codex plan-approval-metadata-must-list-actual-review-a
description: Plan approval metadata must list actual review artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, review-process, gates]
---

Plans claiming review artifacts (e.g., scripts/review/results/plan-2601-claude.md) but leaving them missing fail the hard gate. Attested file existence + listed artifacts must match. If artifacts don't exist yet, either create them before approval or remove the acceptance criterion claiming they are posted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
