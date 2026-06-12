---
name: crossprovider codex enforcement-verification-scripts-not-present-in-
description: Enforcement/verification scripts not present in sparse worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [scripts, sparse-checkout, worktree, verification]
---

Ingest worktrees may be sparse checkouts missing scripts like `check-no-conflict-markers.sh` or legal-scan scripts. Expected by the hardened contract but may be unavailable. Fall back to direct `grep` or `git ls-tree` scans or note the gate as UNAVAILABLE rather than assuming PASS.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
