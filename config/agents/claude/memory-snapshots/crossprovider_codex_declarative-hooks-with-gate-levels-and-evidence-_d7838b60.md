---
name: crossprovider codex declarative-hooks-with-gate-levels-and-evidence-
description: Declarative hooks with gate levels and evidence trails
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, enforcement, audit-trail]
---

Replace prose rule enforcement with YAML-declared hooks: each hook specifies script path, gate level (hard=block|soft=warn), timeout_s, and description. Write structured evidence YAML to assets/WRK-NNN/evidence/ for audit trail. Enables programmatic enforcement and troubleshooting. Introduced in WRK-1316 stage-transition hardening.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
