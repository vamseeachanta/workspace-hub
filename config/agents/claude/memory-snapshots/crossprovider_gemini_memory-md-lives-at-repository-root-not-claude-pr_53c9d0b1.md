---
name: crossprovider gemini memory-md-lives-at-repository-root-not-claude-pr
description: MEMORY.md lives at repository root, not ~/.claude/projects/-mnt-.../memory/
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [memory, paths, portability]
---

Multiple plans hallucinated machine-specific absolute paths like `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md`. The actual file is at the repo root. Memory rule files (AGENTS.md, GEMINI.md) define governance, not global `~/.claude/CLAUDE.md`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
