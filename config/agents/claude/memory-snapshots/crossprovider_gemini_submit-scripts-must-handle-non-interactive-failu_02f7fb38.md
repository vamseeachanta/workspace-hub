---
name: crossprovider gemini submit-scripts-must-handle-non-interactive-failu
description: Submit scripts must handle non-interactive failures safely
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [script-robustness, cross-agent, shell-safety]
---

Scripts like `submit-to-gemini.sh` must explicitly exit with non-zero status on failure (not rely on final echo's exit code), use safe variable expansion like `"${VAR:-}"` to handle missing args under `set -u`, and use `git -C` to ensure repo context when called from arbitrary directories by agents.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
