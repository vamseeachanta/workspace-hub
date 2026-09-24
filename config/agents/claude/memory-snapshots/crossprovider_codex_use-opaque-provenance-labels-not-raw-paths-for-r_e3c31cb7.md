---
name: crossprovider codex use-opaque-provenance-labels-not-raw-paths-for-r
description: Use opaque provenance labels, not raw paths, for repo-safe queue rows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, data-safety, repo-invariant]
---

Pattern is `source-root:*` or `source-ref:*` labels with runtime-only resolution via resolver map. Existing queues contain raw `/mnt/ace/...` path leaks; cleanup plans must include normalization of legacy absolute-path and `source-local:` values, not just field-fill on missing provenance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
