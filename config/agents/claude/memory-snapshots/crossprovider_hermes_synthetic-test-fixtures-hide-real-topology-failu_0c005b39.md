---
name: crossprovider hermes synthetic-test-fixtures-hide-real-topology-failu
description: Synthetic test fixtures hide real topology failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-gap, worktree, topology]
---

Tests using `tmp_path/.git/hooks` pass while real git worktree/sparse-checkout topologies fail. Test fixtures must model actual file structures: worktree `.git` as file, common-dir linkage, sparse-checkout materialization. False-positive green tests delay defect discovery by weeks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
