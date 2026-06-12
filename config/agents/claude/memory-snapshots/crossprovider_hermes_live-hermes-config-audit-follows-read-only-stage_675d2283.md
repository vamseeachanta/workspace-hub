---
name: crossprovider hermes live-hermes-config-audit-follows-read-only-stage
description: Live Hermes config audit follows read-only + staged-changes pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, config-audit, safety-pattern]
---

When gathering intelligence on ~/.hermes/config.yaml mid-session, never mutate live config directly. Instead, stage changes in a separate template file and surface for review. This prevents runtime disruption during audit/planning phases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
