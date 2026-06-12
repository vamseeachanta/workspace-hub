---
name: crossprovider hermes github-api-bulk-queries-timeout-on-large-issue-s
description: GitHub API bulk queries timeout on large issue sets
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, performance, tooling-limits]
---

Single `gh issue list` queries for 800+ issues timeout after ~300s; collection requires batching or paced requests. Tier-1 workspace-hub has 815 open issues; bulk collection without workaround gets killed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
