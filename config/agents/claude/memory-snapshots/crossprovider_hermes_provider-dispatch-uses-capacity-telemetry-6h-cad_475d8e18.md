---
name: crossprovider hermes provider-dispatch-uses-capacity-telemetry-6h-cad
description: Provider dispatch uses capacity telemetry ~6h cadence, not rigid per-provider rules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-dispatch, capacity-management, ai-infrastructure]
---

Shifted from static "3 lanes per provider" to capacity-aware dispatch refreshing telemetry every ~6 hours. Claude Max capacity (USD $200/mo) fluctuates significantly within reset periods—observed ~40% remaining 36h before reset. Rigid lane provisioning misses optimization and wastes budget near reset; dispatch should follow live telemetry, not hard quotas.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
