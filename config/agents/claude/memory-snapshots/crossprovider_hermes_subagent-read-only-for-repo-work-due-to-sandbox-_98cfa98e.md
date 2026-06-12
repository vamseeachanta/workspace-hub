---
name: crossprovider hermes subagent-read-only-for-repo-work-due-to-sandbox-
description: Subagent read-only for repo work due to sandbox limits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [coordination, subagent-pattern, git-operations]
---

Delegate complex multi-repo analysis to subagents for recon/synthesis only. Main session must perform all writes, tests, commits, pushes, and PR operations—subagent sandbox blocks file operations needed for implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
