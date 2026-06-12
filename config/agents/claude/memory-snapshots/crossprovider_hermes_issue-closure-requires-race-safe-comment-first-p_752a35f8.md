---
name: crossprovider hermes issue-closure-requires-race-safe-comment-first-p
description: Issue closure requires race-safe comment-first pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github, race-safety, issue-lifecycle]
---

gh issue close --comment silently drops evidence comments if issue is already closed; pattern is post comment via separate gh api call first, then close issue separately. Prevents evidence loss on concurrent close operations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
