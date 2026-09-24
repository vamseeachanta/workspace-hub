---
name: crossprovider codex verification-scripts-may-not-exist-in-worktree-c
description: Verification scripts may not exist in worktree checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, verification, scripts, tooling]
---

The hardened ingest contract names specific enforcement scripts (check-no-conflict-markers.sh, legal-sanity-scan.sh), but they may not be present in all worktree clones. Verify script paths before relying on them; have fallback inspection logic (e.g., rg grep for conflict markers) if the script is absent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
