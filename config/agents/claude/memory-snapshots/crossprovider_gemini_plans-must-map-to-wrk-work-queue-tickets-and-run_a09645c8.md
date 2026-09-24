---
name: crossprovider gemini plans-must-map-to-wrk-work-queue-tickets-and-run
description: Plans must map to WRK-* work queue tickets and run legal-sanity-scan.sh
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gates, work-queue, legal]
---

Required gates: (1) create/map a `WRK-*` ticket in `.claude/work-queue/` before execution, (2) include `scripts/legal/legal-sanity-scan.sh` in acceptance criteria. Omitting either violates governance.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
