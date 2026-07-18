---
name: crossprovider codex worktree-contamination-during-parallel-audits-pr
description: Worktree contamination during parallel audits prevents accurate assessment
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [git, process, testing]
---

Shared checkout with concurrent writers allows implementation changes to pollute supposedly-isolated audit lanes, causing cascading test failures. Isolated worktrees or serialized write phases are required; audit findings against contaminated state are unreliable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
