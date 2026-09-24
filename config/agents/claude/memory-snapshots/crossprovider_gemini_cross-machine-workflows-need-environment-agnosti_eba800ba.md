---
name: crossprovider gemini cross-machine-workflows-need-environment-agnosti
description: Cross-machine workflows need environment-agnostic paths
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [paths, cross-machine, sync]
---

Absolute paths like `~/.claude/projects/-mnt-local-analysis-workspace-hub/` break when moving between machines. Plans targeting cross-machine sync must use environment variables (e.g., `$MEMORY_HOME`), repo-relative paths, or shell expansion.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
