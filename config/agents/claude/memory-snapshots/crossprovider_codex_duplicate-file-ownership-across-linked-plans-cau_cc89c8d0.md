---
name: crossprovider codex duplicate-file-ownership-across-linked-plans-cau
description: Duplicate file ownership across linked plans causes silent misses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-coordination, artifact-ownership, multi-issue-plans]
---

When multiple issues claim responsibility for creating the same file (e.g., #605, #606, #609 all claimed orcawave_asset_resolver.py), neither actually creates it because coordination is implicit. Linked plans must explicitly assign file ownership or coordinate via shared acceptance criteria that verify the artifact exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
