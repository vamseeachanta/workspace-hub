---
name: crossprovider codex immutable-baseline-rev-0-requires-exact-commit-c
description: Immutable baseline (Rev-0) requires exact commit cutoff and explicit blob allowlist
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [immutable-baseline, git-integrity, mutation-testing]
---

When freezing a baseline snapshot, specify the exact commit SHA cutoff and maintain an allowlist with entries {repo, path, git_blob_sha, sha256, solver, run, evidence_role}; post-cutoff artifacts cannot be added retroactively. Mutation tests must hash all declared files (including pack manifests and all sidecars) to detect any post-hoc changes. Without exact boundaries, later revisions can silently swap evidence or mutate accepted artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
