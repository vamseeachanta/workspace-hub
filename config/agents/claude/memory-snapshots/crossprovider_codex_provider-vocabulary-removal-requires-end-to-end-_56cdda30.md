---
name: crossprovider codex provider-vocabulary-removal-requires-end-to-end-
description: Provider vocabulary removal requires end-to-end migration, not config-only deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provider-migration, label-lifecycle, breaking-changes]
---

Removing a provider label (gemini→agy) leaves stale labels on active issues and may break routing if unknown-provider fallback defaults to auto-routable. Must audit: stale labels in flight, unknown-provider behavior in resolve logic, and all code paths before removing from config.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
