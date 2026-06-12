---
name: crossprovider hermes ci-trigger-gaps-on-contract-only-changes
description: CI trigger gaps on contract-only changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-cd, repo-structure, test-coverage]
---

When adding repo-structure enforcement via config files or documentation, CI workflows may not trigger if they only watch `**/*.py` and related code patterns. Verify workflow includes config/ and docs/standards/ paths or contract changes won't run tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
