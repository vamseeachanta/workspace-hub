---
name: crossprovider codex harness-integration-tests-miss-shell-level-defec
description: Harness integration tests miss shell-level defects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, harness, integration-testing, tdd-scope]
---

Unit tests of core Python logic do not catch bugs in shell script path resolution, multi-repo iteration completeness, or repo-specific config extraction. Harness TDD must span end-to-end flows (enumerate all repos, exercise actual shell extraction, verify exit codes) not just isolated core logic modules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
