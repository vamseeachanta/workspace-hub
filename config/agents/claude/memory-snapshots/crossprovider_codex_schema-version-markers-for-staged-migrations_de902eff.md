---
name: crossprovider codex schema-version-markers-for-staged-migrations
description: Schema version markers for staged migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-evolution, yaml, backwards-compatibility]
---

When evolving YAML schemas for orchestration evidence, use version fields (e.g., `metadata_version: 1`) to distinguish canonical from legacy formats. Apply different validation rules per version, enabling backward compatibility and gradual schema rollout without breaking existing items.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
