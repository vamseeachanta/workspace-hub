---
name: crossprovider gemini silent-success-in-shell-pipelines-when-last-comm
description: Silent success in shell pipelines when last command succeeds
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-scripting, cross-agent-robustness, error-handling]
---

When a script using `set -euo pipefail` chains multiple commands where an earlier command fails but the last is a benign command (e.g., `echo`), the script exits with code 0 (success) masking the earlier failure. This causes orchestrator agents to treat failed operations as succeeded. Always explicitly propagate error codes: add `exit "${exit_code:-1}"` at the bottom of scripts that chain error-prone commands.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
