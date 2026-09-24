---
name: crossprovider gemini registry-workstation-config-changes-cascade-thro
description: Registry/workstation config changes cascade through multiple downstream consumers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [registry, config-coupling, impact-analysis, consumer-inventory]
---

Adding a workstation entry to central registry affects 5+ downstream scripts (status, monitoring, readiness checks, scheduling, health checks). Inventory and disposition each consumer before implementation; document which remain unchanged to prevent silent breakage.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
