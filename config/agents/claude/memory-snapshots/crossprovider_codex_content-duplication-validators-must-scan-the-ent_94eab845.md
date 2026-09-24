---
name: crossprovider codex content-duplication-validators-must-scan-the-ent
description: Content duplication validators must scan the entire target repository tree, not just expected paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, corpus, duplication-detection, edge-cases]
---

Path-limited validators (scanning only `wikis/marine-engineering/`) miss false-positives in `wikis/asset-management/`, `wikis/engineering/`, etc. Repo-wide tree traversal is required for reliable extraction deduplication baselines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
