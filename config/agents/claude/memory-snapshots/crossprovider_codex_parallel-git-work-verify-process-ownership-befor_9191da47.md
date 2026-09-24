---
name: crossprovider codex parallel-git-work-verify-process-ownership-befor
description: Parallel Git work: verify process ownership before terminating background audit commands
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, safety-pattern, git-locks]
---

When another session holds active Git locks on a shared repo, stay read-only. Verify process ownership before killing background audit commands; terminating sibling work can disrupt parallel sessions and create race conditions on shared resources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
