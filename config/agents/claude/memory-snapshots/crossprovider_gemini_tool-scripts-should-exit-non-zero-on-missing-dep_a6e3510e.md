---
name: crossprovider gemini tool-scripts-should-exit-non-zero-on-missing-dep
description: Tool scripts should exit non-zero on missing dependencies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scripting, exit-codes, agent-compatibility]
---

Scripts invoked by agents must exit with non-zero code when critical tools (CLI, python3, etc.) are missing, not exit 0 with markdown error output. Agents expect failure codes to detect issues; exit 0 silently breaks caller error handling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
