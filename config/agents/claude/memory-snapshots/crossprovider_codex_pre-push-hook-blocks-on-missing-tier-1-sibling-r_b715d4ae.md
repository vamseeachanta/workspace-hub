---
name: crossprovider codex pre-push-hook-blocks-on-missing-tier-1-sibling-r
description: Pre-push hook blocks on missing tier-1 sibling repos and rewrites files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pre-push-hooks, sparse-checkouts, git-hazards]
---

The repository's pre-push hook fails when tier-1 sibling directories (assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing) are absent from an isolated worktree. It may also rewrite tracked files (e.g., coverage summaries) during failure; restore these manually before re-attempting push.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
