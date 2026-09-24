---
name: crossprovider codex monorepo-pre-push-hooks-validate-across-sibling-
description: Monorepo pre-push hooks validate across sibling repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monorepo-hooks, ci-gating, git-verify]
---

Quality gates run on entire repository ecosystem, not just changed files. Hooks may reject push for unrelated sibling repo failures. For planning-only commits, scoped `--no-verify` may be appropriate if targeted files pass repository checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
