---
name: crossprovider hermes refresh-provider-capacity-telemetry-every-6-hour
description: Refresh provider capacity telemetry every 6 hours, not static routing rules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-provider, quota-aware, telemetry]
---

Provider capacity and daily quotas change; static routing rules (e.g. 'always use Claude for planning') become stale within hours. Before launching each work wave, check live capacity/usage telemetry and replan provider routing. Hermes/Codex/Claude/Gemini budgets shift throughout the day.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
