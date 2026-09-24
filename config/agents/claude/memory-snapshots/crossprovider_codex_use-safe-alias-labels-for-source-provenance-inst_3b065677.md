---
name: crossprovider codex use-safe-alias-labels-for-source-provenance-inst
description: Use safe alias labels for source provenance instead of mount paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, security, data-handling]
---

When preserving source-root context, emit safe labels (e.g., `safe_source_root_label`) instead of mount paths. Maintains downstream traceability while avoiding infrastructure details. Solution pattern from provenance and licensing work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
