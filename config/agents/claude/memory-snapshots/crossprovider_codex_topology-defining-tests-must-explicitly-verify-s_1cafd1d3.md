---
name: crossprovider codex topology-defining-tests-must-explicitly-verify-s
description: Topology-defining tests must explicitly verify shape, not just accept/reject
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [test-coverage, git-topology, regression-testing]
---

Tests named for specific Git topology (e.g., squash, branch deletion, orphan commit detection) must assert the topology exists, not just that validation succeeds or fails. Absence of shape verification allows refactored fixtures to pass without exercising the intended regression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
