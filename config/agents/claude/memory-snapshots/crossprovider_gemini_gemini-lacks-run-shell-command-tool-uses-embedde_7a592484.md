---
name: crossprovider gemini gemini-lacks-run-shell-command-tool-uses-embedde
description: Gemini lacks run_shell_command tool; uses embedded Python instead
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-provider-diff, gemini-limitation, dispatch-constraint]
---

Gemini cannot execute shell commands via `run_shell_command` tool (returns unavailable error despite core-instruction claims), blocking overnight unattended shell automation. Compensates with embedded `<execute_ipython>` blocks for Python execution, which Claude lacks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
