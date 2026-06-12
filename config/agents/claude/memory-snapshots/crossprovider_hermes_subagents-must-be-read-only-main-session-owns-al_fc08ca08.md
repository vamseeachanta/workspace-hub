---
name: crossprovider hermes subagents-must-be-read-only-main-session-owns-al
description: Subagents must be read-only; main session owns all writes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-architecture, sandbox-limits, git-serialization]
---

Subagents operate in sandboxed environments that prevent file writes and git commits. Delegate analysis/recon/synthesis to subagents, but perform all repo modifications (commits, pushes, PRs, test runs with side effects) in the main session. Otherwise writes silently fail or trigger permission prompts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
