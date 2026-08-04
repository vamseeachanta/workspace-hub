---
name: crossprovider codex pytest-lane-aware-configuration-trades-startup-c
description: pytest lane-aware configuration trades startup cost for coverage preservation
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [pytest, performance, testing]
---

Make per-lane plugin behavior conditional (regression analysis only after real test runs, benchmark metadata only on benchmark runs, randomly plugin only in full-suite lane) to speed collect-only and fast paths without deleting signal. Measure on idle box only (load < 1.5).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
