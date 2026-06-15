---
name: crossprovider codex stacked-pr-chain-pattern-for-sequential-corpus-i
description: Stacked-PR chain pattern for sequential corpus ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ci-workflow, stacked-pr, corpus-ingest, llm-wiki]
---

Process publishers sequentially (not in parallel) in `--chain` mode: each publisher's branch builds from the previous publisher's branch (resolve via `git ls-remote --heads origin`, default to origin/main if absent). Each PR bases against the prior PR's branch, so PRs merge in order without cross-publisher duplicates on shared files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
