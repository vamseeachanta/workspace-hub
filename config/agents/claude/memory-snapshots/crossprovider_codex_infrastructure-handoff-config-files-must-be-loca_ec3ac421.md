---
name: crossprovider codex infrastructure-handoff-config-files-must-be-loca
description: Infrastructure handoff: config files must be locally saved, not ephemeral
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [infrastructure, handoff, configuration]
---

When handing off setup work between machines, confirm config files are written to the target machine, not left in chat/email. Explicitly verify persistence before marking handoff ready. Identify blocking steps (e.g., passwordless sudo availability) upfront.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
