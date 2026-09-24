---
name: crossprovider codex diagnostic-metric-naming-must-disclose-approxima
description: Diagnostic metric naming must disclose approximation status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, simulation-reporting, clarity]
---

When reports name metrics that differ from canonical engineering definitions (e.g., 'Tactical diameter proxy' for a 3.62° heading change vs. true 180° tactful diameter), markdown reports and docstrings must explicitly mark them as approximate, diagnostic-only, or proxy. Unmarked diagnostic metrics cause readers to incorrectly grep for canonical names and draw wrong conclusions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
