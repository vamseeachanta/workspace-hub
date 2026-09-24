---
name: crossprovider codex cross-repo-contract-test-coverage-must-match-act
description: Cross-repo contract test coverage must match actual imports, not inferred patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-repo-testing, contract-tests, coverage-derivation]
---

Mirroring test coverage from a related repo (e.g., digitalmodel) without auditing actual import surface in the target repo (e.g., assethold) creates false confidence. Real breakages are missed if they touch symbols not in the mirrored test set. Derive contract scope from `grep -r` actual imports, not analogy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
