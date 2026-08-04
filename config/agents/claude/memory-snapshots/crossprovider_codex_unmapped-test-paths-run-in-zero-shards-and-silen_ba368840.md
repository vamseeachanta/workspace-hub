---
name: crossprovider codex unmapped-test-paths-run-in-zero-shards-and-silen
description: Unmapped test paths run in zero shards and silently report green
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, ci, sharding, correctness]
---

In domain-partitioned CI (digitalmodel pattern), a test file matching no domain's root list runs in zero shards and silently succeeds. DOMAINS.md must prove totality: every pytest-shaped file owns exactly one domain or is explicitly excluded.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
