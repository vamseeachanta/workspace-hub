---
name: crossprovider codex residue-classification-by-provenance-for-accurat
description: Residue classification by provenance for accurate auditing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [auditing, qa-patterns, git-housekeeping]
---

When auditing cleanup, distinguish task-created residue from pre-existing canonical state (stashes, locks, divergence) to avoid false 'blocker' claims. Record what is CLEAN, EXPECTED (shared stashes from other sessions), and UNEXPECTED (unrelated to the current task) separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
