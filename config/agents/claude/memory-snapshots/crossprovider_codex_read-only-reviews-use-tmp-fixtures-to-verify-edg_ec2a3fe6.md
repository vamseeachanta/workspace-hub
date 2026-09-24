---
name: crossprovider codex read-only-reviews-use-tmp-fixtures-to-verify-edg
description: Read-only reviews use `/tmp` fixtures to verify edge-case behavior without repo mutation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-technique, testing, verification, read-only]
---

When unable to modify the repo, create isolated `/tmp` fixtures to test whether code enforces intended invariants (e.g., fail-closed validation, edge-case classification). This surfaces behavioral defects code review alone misses. Document fixture commands in findings; clean up residue before closeout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
