---
name: crossprovider gemini refactored-modules-require-dual-import-path-alig
description: Refactored modules require dual import-path alignment
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [refactoring, test-maintenance, api-stability]
---

When refactoring modules (e.g., moving NPV methods from `ProductionAPI12Analysis` to a `financial` submodule), both the production API entry points AND all test import statements must be realigned. Stale test imports with non-existent paths create collection-succeeds-execution-fails scenarios.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
