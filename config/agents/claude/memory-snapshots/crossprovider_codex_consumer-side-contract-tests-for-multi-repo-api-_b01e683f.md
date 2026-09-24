---
name: crossprovider codex consumer-side-contract-tests-for-multi-repo-api-
description: Consumer-side contract tests for multi-repo API stability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, multi-repo, api-contracts, pytest]
---

Maintain tests/contracts/ in each importing repo (e.g., digitalmodel, worldenergydata) that import and introspect the provider's (assetutilities) actual public API using real dependencies — no mocks. Use @pytest.mark.contracts marker with pytest_runtest_makereport hook to enrich failures with version + symbol info, catching silent API breakage early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
