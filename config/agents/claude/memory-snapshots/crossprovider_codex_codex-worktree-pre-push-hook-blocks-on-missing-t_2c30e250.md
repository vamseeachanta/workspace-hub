---
name: crossprovider codex codex-worktree-pre-push-hook-blocks-on-missing-t
description: Codex worktree pre-push hook blocks on missing tier-1 repos
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex-worktree, pre-push-hook, missing-dependencies]
---

Codex isolated worktrees lack tier-1 sibling repos (`assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `OGManufacturing`). Pre-push hooks fail importing `yaml` from `scripts/quality/check_config_drift.py` or referencing these repos. Normal push blocks; commits still land locally but require human intervention to merge or push via main session.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
