---
name: crossprovider gemini path-confusion-pattern-workspace-hub-state-is-re
description: Path confusion pattern: workspace-hub state is repo-local, not ~/.claude/
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workspace-hub, paths, repo-structure]
---

`MEMORY.md`, `.claude/work-queue/`, and `.claude/skills/` are at the repository root. Plans and scripts should reference repo-local paths, not global `~/.claude/projects/<hash>/` or `~/.claude/` unless explicitly managing global config.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
