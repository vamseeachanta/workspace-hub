---
name: crossprovider codex inter-agent-shell-scripts-fail-silently-with-exi
description: Inter-agent shell scripts fail silently with exit code 0
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-script-automation, exit-codes, cross-agent-reliability]
---

Scripts invoked cross-agent (e.g., submit-to-codex.sh) often report exit code 0 even when inner operations fail (codex execution errors, validation failures), making failure detection impossible for caller agents. Audit all inter-agent scripts for deterministic non-zero exit codes on error paths and avoid hard runtime dependencies (python3, specific binaries).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
