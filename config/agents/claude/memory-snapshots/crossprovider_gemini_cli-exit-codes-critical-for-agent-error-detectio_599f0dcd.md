---
name: crossprovider gemini cli-exit-codes-critical-for-agent-error-detectio
description: CLI exit codes critical for agent error detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-agent-scripts, exit-codes, error-handling]
---

Scripts called by orchestrators must exit non-zero on failure, including missing dependencies. Exiting 0 when CLI tool is absent creates false positives in agent error handling. Always validate `command -v <tool>` with `exit 1` on failure, not silent success.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
