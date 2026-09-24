---
name: crossprovider codex submodule-commits-must-land-inside-the-submodule
description: Submodule commits must land inside the submodule before parent pointer update
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-submodules, migrations, commit-order]
---

When a migration touches both a submodule's local state and the parent repo's pointer to it, commit changes inside the submodule first (`git -C submodule commit`), then stage and commit the pointer update in the parent. Reversing the order creates transient state where the pointer is stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
