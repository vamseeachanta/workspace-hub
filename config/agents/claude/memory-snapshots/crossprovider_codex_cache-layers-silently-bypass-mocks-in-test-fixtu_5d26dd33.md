---
name: crossprovider codex cache-layers-silently-bypass-mocks-in-test-fixtu
description: Cache layers silently bypass mocks in test fixture design
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, caching]
---

Deterministic test fixtures via mocking can fail if the tested component checks cache (disk or in-memory) before calling the mocked function. The cache hit prevents the mock from ever executing. Audit the full call chain including all caching layers to identify all external dependencies that require fixtures, not just the primary API.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
