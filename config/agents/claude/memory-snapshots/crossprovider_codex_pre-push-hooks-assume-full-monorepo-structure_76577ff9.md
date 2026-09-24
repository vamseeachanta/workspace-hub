---
name: crossprovider codex pre-push-hooks-assume-full-monorepo-structure
description: Pre-push hooks assume full monorepo structure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, monorepo, ci-cd]
---

Isolated bundles and worktrees may fail pre-push hooks that expect sibling tier-1 repos (assetutilities, digitalmodel, etc.) to exist, even though the hook's review evidence passes. Isolated work may need `--no-verify` or hook redesign.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
