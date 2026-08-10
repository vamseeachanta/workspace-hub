---
name: crossprovider codex verify-working-tree-against-claimed-baseline-bef
description: Verify working tree against claimed baseline before accepting config measurements
metadata:
  type: reference
  source: codex
  bridged: 2026-08-09
  tags: [adversarial-review, working-tree, measurement, rigor]
---

Before trusting a plan's claims about pytest/collection behavior differences, verify the actual checkout (branch, modified files, lock state) against the stated 'clean origin/main@SHA' baseline. Separate source-file evidence from working-tree-dependent measurements; dirty worktree state can invalidate performance and collection diffs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
