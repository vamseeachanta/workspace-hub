---
name: crossprovider gemini yaml-canonical-pattern-with-drift-detection
description: YAML-canonical pattern with drift detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [yaml, config, validation, automation]
---

When maintaining both YAML and generated Markdown versions of the same config or ledger, make YAML canonical and automate drift checking (via validator script or pre-commit hook) so they never silently diverge. Prevents inconsistency between machine-readable source and human-readable mirror.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
