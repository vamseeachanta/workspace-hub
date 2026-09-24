---
name: crossprovider codex generator-discovery-via-literal-text-search-crea
description: Generator discovery via literal-text search creates false-green paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, generators, static-analysis]
---

Searching for exact string literals like 'docs', 'api', '.html' misses generators using helper functions, constructed paths, or different case. Fail-closed discovery requires AST-based analysis or explicit registry with validation tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
