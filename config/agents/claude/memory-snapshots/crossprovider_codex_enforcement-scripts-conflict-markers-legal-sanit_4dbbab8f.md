---
name: crossprovider codex enforcement-scripts-conflict-markers-legal-sanit
description: Enforcement scripts (conflict-markers, legal-sanity-scan) missing from worktree branches
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [verification-gate, tooling, missing-scripts]
---

The hardened contract verification gate references scripts/enforcement/check-no-conflict-markers.sh and scripts/legal/legal-sanity-scan.sh, but these are absent in temporary ingest worktrees (likely on origin/main only). Verification then fails on 'script not found' rather than actual markers. Either ship scripts to worktrees or make enforcement optional in worktree contexts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
