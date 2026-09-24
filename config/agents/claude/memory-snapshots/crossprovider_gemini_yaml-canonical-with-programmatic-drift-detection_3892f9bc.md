---
name: crossprovider gemini yaml-canonical-with-programmatic-drift-detection
description: YAML canonical with programmatic drift detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-architecture, state-management, validation-patterns]
---

When state requires both machine-readable and human-readable forms, store canonical data in YAML and generate Markdown views from it. Use automated `--check` scripts that fail if Markdown and YAML diverge—this prevents hand-edit corruption and keeps truth synchronized across representations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
