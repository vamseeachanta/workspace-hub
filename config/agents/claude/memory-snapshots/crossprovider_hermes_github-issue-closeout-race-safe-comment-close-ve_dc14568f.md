---
name: crossprovider hermes github-issue-closeout-race-safe-comment-close-ve
description: GitHub issue closeout: race-safe comment→close→verify sequence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github, issue-management, race-condition, closeout]
---

Immediate `gh issue close` silently drops comments posted in same session. Race-safe pattern: (1) write comment to temp file, (2) `gh issue comment --body-file`, (3) `gh issue close`, (4) `gh issue view` to verify final state. Prevents comment loss and enables post-close verification.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
