---
name: crossprovider hermes codex-orchestration-isolated-worktrees-stdin-clo
description: Codex orchestration: isolated worktrees, stdin closure, sandbox bypass
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, provider-integration, worktree-pattern]
---

Maintain 3-5 concurrent Codex lanes in isolated worktrees at `/mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN/`. Write prompts to /tmp/. CLOSE STDIN immediately after exec (Codex hangs on 'Reading additional input from stdin...' otherwise). Launch with `--dangerously-bypass-approvals-and-sandbox` to work around bwrap loopback error; scope limited to worktree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
