---
name: crossprovider codex encode-policies-as-cli-flags-not-prose
description: Encode policies as CLI flags, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gating, testing, cli-design]
---

Policy decisions like 'block on MEDIUM/HIGH' must be expressed in code (e.g. `-ll` flag in every gating command), not just documented. Prevents silent policy drift and enables test verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
