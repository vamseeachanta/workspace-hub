---
name: crossprovider codex keep-working-transport-until-replacement-validat
description: Keep working transport until replacement validates across restart
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [operations, deployment]
---

Do not remove a working connection path until its replacement passes host-key verification, authentication, restart/reconnect cycles, and unattended dispatch scenarios. Document the transition boundary to prevent accidental removal during validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
