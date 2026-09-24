---
name: crossprovider codex nested-session-provider-invocation-is-blocked
description: Nested-session provider invocation is blocked
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [platform-constraint, nested-session, multi-agent]
---

Invoking the same provider CLI from within that provider's session fails (e.g., Claude → Claude). This platform constraint breaks fan-out orchestration when one provider tries to spawn agents of the same provider in multi-agent systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
