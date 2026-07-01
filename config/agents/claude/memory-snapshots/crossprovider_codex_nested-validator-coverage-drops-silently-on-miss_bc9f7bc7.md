---
name: crossprovider codex nested-validator-coverage-drops-silently-on-miss
description: Nested validator coverage drops silently on missing paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [validator-composition, ci-coverage, error-semantics]
---

When validator A scans paths for validator B or wraps it, skip-on-not-found behavior can silently drop coverage. Nested validators must fail explicitly on missing paths; missing→error, not skip.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
