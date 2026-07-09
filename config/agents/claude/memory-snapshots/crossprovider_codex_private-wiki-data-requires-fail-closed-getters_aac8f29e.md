---
name: crossprovider codex private-wiki-data-requires-fail-closed-getters
description: Private wiki data requires fail-closed getters
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [wiki-integration, provenance, fail-closed, private-data]
---

When code consumes private wiki pages or registries, use explicit fail-closed getters that cite sources. Never silent fallback to stale defaults; test provenance consistency and verify public code cannot leak private assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
