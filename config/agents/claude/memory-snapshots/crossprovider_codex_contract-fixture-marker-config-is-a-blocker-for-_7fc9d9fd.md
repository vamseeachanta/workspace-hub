---
name: crossprovider codex contract-fixture-marker-config-is-a-blocker-for-
description: Contract/fixture marker config is a blocker for cross-repo gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest-markers, cross-repo-testing]
---

Cross-repo test gates running `pytest -m contracts` will fail if downstream repos don't have the marker defined in their pytest config. This must be verified and added to each repo BEFORE the integration runner is created (WRK-1091 phase 2 showed assethold missing marker config).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
