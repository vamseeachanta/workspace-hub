---
name: crossprovider codex workspace-hub-pre-push-hook-fails-in-isolated-wo
description: workspace-hub pre-push hook fails in isolated worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, workspace-hub, infrastructure]
---

Pre-push hook fails consistently when isolated worktrees lack tier-1 sibling repos (assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing). This is expected and documented; push with `GIT_PRE_PUSH_SKIP=1` or `--no-verify` when working in isolated environments, and document the blocker in issue comments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
