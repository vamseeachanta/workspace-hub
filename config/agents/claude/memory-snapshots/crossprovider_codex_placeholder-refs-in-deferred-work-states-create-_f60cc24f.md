---
name: crossprovider codex placeholder-refs-in-deferred-work-states-create-
description: Placeholder refs in deferred-work states create untracked work debt
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [workflow-design, governance, issue-tracking]
---

When a workflow defers work via strings like 'future-promotion-required' or 'future-approval-needed' instead of concrete GitHub issue refs, the deferred work becomes invisible to dependency tracking and issue-planning gates. Gate tests cannot enforce that deferred work exists until refs are real, link-resolvable issues with their own status labels.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
