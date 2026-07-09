---
name: crossprovider codex operational-content-gating-explicit-bounds-befor
description: Operational content gating: explicit bounds before approval gates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [governance, plan-review, gates]
---

Plans that defer operational/measured/private content until an approval gate (e.g., #61 durable-output gate) must explicitly block all output paths, persistent metrics, and store writes until that gate has `status:plan-approved`. Prose saying 'deferred' is insufficient; the plan must name what is blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
