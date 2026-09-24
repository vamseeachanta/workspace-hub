---
name: crossprovider codex append-only-hook-installer-with-string-based-ide
description: Append-only hook installer with string-based idempotence is self-perpetuating
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [installer, idempotence, append-only, enforcement]
---

Installers that append blocks to a hook using `cat >>` with idempotence checks on string presence (not reachability) create unreachable code if a hook ends in unconditional exit before the appended block. Re-running the installer will not repair the damage because the idempotence gate tests for string presence, not execution reachability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
