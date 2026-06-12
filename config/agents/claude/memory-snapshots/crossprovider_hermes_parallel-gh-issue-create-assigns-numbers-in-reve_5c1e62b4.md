---
name: crossprovider hermes parallel-gh-issue-create-assigns-numbers-in-reve
description: Parallel gh issue create assigns numbers in reverse arrival order
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, parallel-create-race, issue-numbering]
---

`gh issue create &` in parallel assigns issue numbers in reverse arrival order, not creation order. Batch-created issues #2762-#2765 may have final numbers ≠ intended sequence. Audit via `gh issue list --json number,title` post-batch, not by creation timestamp.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
