---
name: crossprovider hermes subagent-repo-work-is-read-only-main-session-han
description: Subagent repo work is read-only; main session handles all writes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-agent-patterns, sandbox-limits, work-distribution]
---

Subagents cannot write files to repos due to sandbox limits. Use them only for analysis, reconnaissance, synthesis. Main session must perform all file writes, test runs, commits, pushes, issue comments, and PR operations. Partition work to respect this boundary.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
