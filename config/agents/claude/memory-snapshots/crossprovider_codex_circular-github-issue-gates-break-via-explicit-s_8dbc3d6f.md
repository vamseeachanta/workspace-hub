---
name: crossprovider codex circular-github-issue-gates-break-via-explicit-s
description: Circular GitHub issue gates break via explicit stage-name separation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [github-workflow, issue-architecture, dependency-management]
---

When one issue must complete by 'linking to another issue' and that linked issue blocks on the first, a circular dependency forms. Break it by explicitly separating stages: issue A produces a 'discussion-draft release candidate', issue B produces 'operational readiness package', issue C produces 'final cross-artifact review'. This way A's completion no longer requires C's completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
