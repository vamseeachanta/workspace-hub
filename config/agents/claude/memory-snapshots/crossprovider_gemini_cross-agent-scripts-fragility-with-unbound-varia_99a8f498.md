---
name: crossprovider gemini cross-agent-scripts-fragility-with-unbound-varia
description: Cross-agent scripts fragility with unbound variables and repo context
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, cross-agent-robustness, cli-design]
---

When scripts are called non-interactively by orchestrator agents, `set -u` causes crashes if arguments are missing or shifted incorrectly. Use `${var:-}` for optional args and `git -C "${REPO_ROOT:-.}" ...` to ensure git commands execute in repo context regardless of caller's working directory. Test argument parsing with missing/incomplete flag values.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
