---
name: crossprovider hermes symlink-beats-dual-write-for-agent-repo-artifact
description: Symlink beats dual-write for agent-repo artifact coordination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-agent-coordination, symlink-pattern, artifact-persistence]
---

When agents (Hermes) create skills/scripts that need to be accessed by other tools (Claude Code), symlink from the agent's native directory to the repo's shared directory (git-tracked symlink) maintains a single source of truth and avoids sync drift better than dual-write. Hermes writes to ~/.hermes/skills/, repo tracks symlink to it at .claude/skills/.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
