---
name: crossprovider codex lazy-registry-tests-require-import-forbid-prefix
description: Lazy-registry tests require import-forbid prefix updates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [lazy-loading, test-registration, scheduler-jobs]
---

Lazy-registry tests hard-code import-forbid prefix lists. Adding new scheduler job requires extending forbid pattern to match job module namespace (e.g., worldenergydata.scheduler.jobs.*).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
