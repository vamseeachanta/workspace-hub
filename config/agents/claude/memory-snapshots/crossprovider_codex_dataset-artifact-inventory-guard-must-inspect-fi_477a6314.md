---
name: crossprovider codex dataset-artifact-inventory-guard-must-inspect-fi
description: Dataset/artifact inventory guard must inspect filesystem/git, not just filter supplied list
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [inventory-tracking, governance, edge-cases]
---

Guards that only filter a supplied target list miss accidental writes outside the list scope. Define an explicit inventory seam: pre/post `git diff --name-only` results or snapshot-based comparison. Negative tests must prove unexpected CSV/dataset/report/figure writes outside allowlist are caught and blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
