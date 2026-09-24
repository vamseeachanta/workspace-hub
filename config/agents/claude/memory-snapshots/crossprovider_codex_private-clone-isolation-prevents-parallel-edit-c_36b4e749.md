---
name: crossprovider codex private-clone-isolation-prevents-parallel-edit-c
description: Private clone isolation prevents parallel-edit conflicts during planning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, planning, parallelism]
---

When canonical checkout has active parallel edits, isolate planning to a clean filesystem clone. Only the planning branch owns the plan artifacts and index row. Prevents merge conflicts and allows independent review cycles without blocking parallel sessions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
