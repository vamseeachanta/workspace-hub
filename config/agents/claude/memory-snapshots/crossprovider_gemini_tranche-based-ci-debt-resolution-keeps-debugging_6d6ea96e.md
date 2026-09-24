---
name: crossprovider gemini tranche-based-ci-debt-resolution-keeps-debugging
description: Tranche-based CI debt resolution keeps debugging focused and avoids mega-PRs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scope-management, debt-management, workflow-design]
---

Split multi-category CI fixes (smoke, lint, type, quality) into narrow sequential tranches, each with explicit pass condition and follow-on issue for residual debt. #2459 follows #2448 pattern: smoke unblock complete, defer broader lint/mypy/quality-gate debt to separate scoped issue. Prevents review fatigue and root-cause diagnosis from drowning in 286 errors across 39 files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
