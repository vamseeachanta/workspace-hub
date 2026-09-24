---
name: crossprovider codex test-config-injection-masks-production-default-m
description: Test config injection masks production default mismatches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, contracts, production-gaps]
---

Unit tests that inject custom config (e.g., scheduler job lists, health check paths) never catch production default mismatches. Production paths must be tested without injection. A test that always passes with injected config can fail silently in production when defaults change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
