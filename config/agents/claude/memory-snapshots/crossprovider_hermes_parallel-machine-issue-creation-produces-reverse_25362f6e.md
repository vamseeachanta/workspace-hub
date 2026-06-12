---
name: crossprovider hermes parallel-machine-issue-creation-produces-reverse
description: Parallel machine issue creation produces reverse-number assignment
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, parallel-operations, auditing]
---

Creating N GitHub issues in parallel via `gh issue create &` assigns issue numbers in reverse arrival order; audit via `gh issue list --json title,number` post-batch to verify correct machine→issue mapping.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
