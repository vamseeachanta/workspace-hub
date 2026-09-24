---
name: crossprovider codex expand-sparse-checkout-for-test-referenced-files
description: Expand sparse checkout for test-referenced files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sparse-checkouts, test-infrastructure]
---

Test suites may reference files outside the initial sparse-checkout scope, causing spurious failures. Expand the sparse set to include referenced paths (e.g., config YAML, docs, fixtures) before re-running validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
