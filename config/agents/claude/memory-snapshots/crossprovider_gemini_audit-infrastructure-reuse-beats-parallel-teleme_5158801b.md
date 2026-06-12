---
name: crossprovider gemini audit-infrastructure-reuse-beats-parallel-teleme
description: Audit infrastructure reuse beats parallel telemetry sources
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture, observability, reporting]
---

When adding measurement/telemetry work, extend existing audit scripts and JSON artifacts rather than inventing a second measurement source. Keep numeric source-of-truth in JSON/data files and regenerate derived reports (markdown, dashboards) via code, never hand-edit them.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
