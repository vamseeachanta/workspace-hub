---
name: crossprovider hermes cross-repo-blocking-issue-handoff-structure-and-
description: Cross-repo blocking-issue handoff structure and non-folding directive
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [handoff-pattern, blocking-dependencies, cross-repo]
---

When PR #528 is blocked by unrelated issue #2441, create a separate handoff documenting: implementation summary, readiness matrix for related features, CI blocker rationale, and an explicit 'do not fold this dependency fix into the PR unless explicitly approved' directive to prevent scope creep across repositories.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
