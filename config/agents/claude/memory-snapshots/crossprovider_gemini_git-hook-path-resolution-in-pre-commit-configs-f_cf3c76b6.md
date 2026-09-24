---
name: crossprovider gemini git-hook-path-resolution-in-pre-commit-configs-f
description: Git hook path resolution in pre-commit configs from subdirectories
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-hooks, pre-commit, path-resolution]
---

When configuring hooks in `.pre-commit-config.yaml` at repo root that reference scripts in parent directories, relative paths are calculated from the config file location, not git root. Path `../../scripts/hooks/hook.sh` from assetutilities/ goes up two levels instead of one. Use a path-resolution step or verify via `ls` before committing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
