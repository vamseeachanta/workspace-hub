---
name: crossprovider codex single-canonical-source-prevents-model-selection
description: Single canonical source prevents model-selection confusion
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hermes, model-routing, single-source-of-truth]
---

Hermes with defaults split across config.yaml, template, delegation modes, and quick-commands creates user confusion and silent fallback behavior. Consolidate to one canonical source (template) with sync-driven updates to avoid divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
