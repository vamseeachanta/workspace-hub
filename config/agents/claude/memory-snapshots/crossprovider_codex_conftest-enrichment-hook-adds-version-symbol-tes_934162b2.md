---
name: crossprovider codex conftest-enrichment-hook-adds-version-symbol-tes
description: Conftest enrichment hook adds version+symbol+test_id to contract failures
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, multi-repo, diagnostics]
---

Use pytest_runtest_makereport hook to prepend diagnostic context (dependency version, imported symbol, test node ID) to multi-repo contract-test failures. Enables rapid diagnosis of which exact API changed between consumer and provider.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
