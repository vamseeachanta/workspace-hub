---
name: crossprovider codex worktree-audits-need-re-verification-in-concurre
description: Worktree audits need re-verification in concurrent multi-agent environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktrees, concurrent-ops, workspace-hub, safe-cleanup]
---

Point-in-time audits of git worktrees for staleness are unreliable when concurrent agents (Hermes, Codex, Claude) are active. Observed stale worktrees may be actively in-use or cleaned up by concurrent agents between early and later audit passes. Always re-run the audit immediately before applying any cleanup actions to ensure state consistency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
