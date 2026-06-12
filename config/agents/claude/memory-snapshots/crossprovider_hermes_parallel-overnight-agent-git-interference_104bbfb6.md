---
name: crossprovider hermes parallel-overnight-agent-git-interference
description: Parallel overnight agent git interference
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, multi-agent, workspace-hub]
---

Multiple Hermes agents running simultaneously (Terminal 1-5) generate untracked files, staged changes, and conflicting git operations. Solution: stash/pull/pop when needed; use git status to identify other-terminal changes before committing own work. Serialize commits if touching same files.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
