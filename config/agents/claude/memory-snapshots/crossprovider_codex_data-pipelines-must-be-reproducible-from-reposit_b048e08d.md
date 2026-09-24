---
name: crossprovider codex data-pipelines-must-be-reproducible-from-reposit
description: Data pipelines must be reproducible from repository sources alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-pipeline, reproducibility, ci-cd]
---

If a publishing pipeline downloads/patches external data before exporting, it cannot be reproduced from repository sources. Either fix the producer or mark the artifact non-reproducible and require manual refresh.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
