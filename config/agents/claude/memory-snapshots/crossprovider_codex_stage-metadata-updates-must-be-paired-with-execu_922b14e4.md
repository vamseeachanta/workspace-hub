---
name: crossprovider codex stage-metadata-updates-must-be-paired-with-execu
description: Stage metadata updates must be paired with executor enforcement code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, integration, testing]
---

Updating stage contract files (YAML metadata, blocking conditions, exit artifacts) without updating the Python/shell code that reads and enforces them creates documentation-only contracts that aren't executed. Both metadata and executor must change together, and tests must verify the integration path, not just the metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
