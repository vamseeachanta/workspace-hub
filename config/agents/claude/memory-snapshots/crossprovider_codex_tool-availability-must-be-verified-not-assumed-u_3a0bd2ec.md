---
name: crossprovider codex tool-availability-must-be-verified-not-assumed-u
description: Tool availability must be verified, not assumed — use managed invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [harness-design, cli-safety, environment]
---

Don't assume tools exist in the environment (e.g., `pip-audit`, `uv audit`). Verify tool availability upfront, check version flags, and declare invocation via managed paths like `uv run --with <tool>` or `uv tool run <tool>` for reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
