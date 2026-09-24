---
name: crossprovider codex approval-markers-are-revision-bound-and-cannot-b
description: Approval markers are revision-bound and cannot be assumed from GitHub labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, revision-bound-markers, gate-verification]
---

A GitHub `status:plan-approved` label can coexist with a missing or stale revision-bound approval marker (e.g., `plan-approved/<issue>.md`). Both must align; label alone is insufficient. Revalidate marker SHA against local branch HEAD and plan file version before implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
