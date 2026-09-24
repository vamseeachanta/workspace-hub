---
name: crossprovider codex git-hook-environment-contract-is-undocumented-an
description: Git hook environment contract is undocumented and unsafe
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, contract-hazards, undocumented-env]
---

`post-commit` hooks receive no parameters and Git does not define a `$GIT_COMMIT` variable for them. Relying on undocumented env vars or `--no-verify` bypasses (which skip `pre-commit` entirely) breaks hook-based detection schemes. Use `git rev-parse HEAD` post-commit instead; add explicit tests for `--no-verify` local commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
