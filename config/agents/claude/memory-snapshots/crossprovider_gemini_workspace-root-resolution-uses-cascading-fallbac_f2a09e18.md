---
name: crossprovider gemini workspace-root-resolution-uses-cascading-fallbac
description: Workspace root resolution uses cascading fallbacks for portability
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash-portability, script-patterns, workspace-resolution]
---

detect_workspace_hub() pattern: check WORKSPACE_HUB env var → script location git rev-parse → hardcoded Windows paths. Enables portable bash scripts that find workspace root across machines (Linux, macOS, Windows Git Bash) without requiring symlinks or environment setup.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
