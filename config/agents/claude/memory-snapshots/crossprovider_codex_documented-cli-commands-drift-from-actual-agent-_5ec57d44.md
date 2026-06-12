---
name: crossprovider codex documented-cli-commands-drift-from-actual-agent-
description: Documented CLI commands drift from actual agent adapter wiring
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cli-interface, adapter-drift, documentation-sync]
---

Work-queue docs advertise commands like `/work add`, `/work clash`, `/work archive` that don't exist in the Codex wrapper script, which only exposes `/work run`, `list`, `approve-batch`, `next`, `status`. Adapter and documentation divergence goes undetected until a user tries the undocumented command.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
