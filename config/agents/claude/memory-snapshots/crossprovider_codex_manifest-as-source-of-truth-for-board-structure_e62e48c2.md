---
name: crossprovider codex manifest-as-source-of-truth-for-board-structure
description: Manifest-as-source-of-truth for board structure
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [kanban, manifest, schema, config]
---

Read board structure from manifest.yaml, not filesystem glob. Detect on-disk boards not in manifest; abort if they have data (data-at-risk), warn if empty. Prevents unmanaged board mutation outside the reconciliation loop.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
