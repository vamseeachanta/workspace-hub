---
name: crossprovider codex parallel-workspace-hub-git-lock-contention-requi
description: Parallel workspace-hub git-lock contention requires serialization strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [parallel-execution, git-safety, workspace-hub]
---

Multiple concurrent agents on workspace-hub race on git locks; symptoms include `[rejected]` pushes, autostash failures, and silent commit drops during retry loops. Mitigation: serialize commits via main session (subagents write only, main commits), use worktrees for parallel branching, or explicit `--no-sync` + `GIT_OPTIONAL_LOCKS=0` gates. Document parallel strategy in branch PR.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
