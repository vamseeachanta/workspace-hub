---
name: crossprovider codex wrk-artifact-synchronization-gate-during-plan-re
description: WRK artifact synchronization gate during plan revisions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, gates, work-queue]
---

When a plan undergoes legitimate revisions (scope simplification, deliverable changes, acceptance criteria updates), the canonical WRK artifact in the work queue must be updated simultaneously. Reviewers treat the WRK artifact as the source of truth for approved plans. If implementation diverges from the artifact (different filenames, scope, or acceptance criteria), it violates the plan-approval gate. Update the artifact as part of the revision cycle, not after implementation starts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
