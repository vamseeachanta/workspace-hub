---
name: crossprovider codex untracked-dependencies-break-pr-boundaries
description: Untracked dependencies break PR boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-workflow, llm-wiki, pr-packaging]
---

Generated code and artifacts left as `??` untracked while imports and manifests reference them. When PR is cut from `git diff origin/main...HEAD`, untracked files are omitted → PR merges with broken imports and missing assets. Must enforce: generated scaffold code tracked or materialized via build system before merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
