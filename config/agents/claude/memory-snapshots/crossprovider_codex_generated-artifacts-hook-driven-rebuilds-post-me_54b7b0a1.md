---
name: crossprovider codex generated-artifacts-hook-driven-rebuilds-post-me
description: Generated artifacts + hook-driven rebuilds = post-merge churn
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, hooks, build-artifacts]
---

Tracked generated files (e.g., `symbol-index.jsonl` in git) combined with `post-merge` hook rebuilds cause worktree churn after every pull if the generated output is not bit-identical. Use untracked cache location, explicit `.gitignore`, or accept rebuild cost transparently; don't mix tracked + regenerated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
