---
name: crossprovider codex codex-cli-non-interactive-mode-has-stdin-regress
description: Codex CLI non-interactive mode has stdin regression
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex-cli, multi-agent-dispatch]
---

When dispatching multi-agent reviews via Codex CLI in non-interactive mode (e.g., via fanout scripts), expect stdin regression. Use native Codex child session or alternate provider as fallback to avoid blocking review cycles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
