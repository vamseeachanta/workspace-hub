---
name: crossprovider codex tier-1-repos-are-separate-git-trees-not-workspac
description: Tier-1 repos are separate git trees, not workspace-hub subdirs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [architecture, tier-1-repos, workspace-hub]
---

Implementation for digitalmodel, assethold, assetutilities, worldenergydata, and aceengineer-website lives in separate Git repos at `/mnt/local-analysis/workspace-hub/<name>/`, not in workspace-hub itself. workspace-hub contains only planning/coordination/routing docs referencing these repos. Issue implementation often requires isolated clones of the target tier-1 repo on the issue branch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
