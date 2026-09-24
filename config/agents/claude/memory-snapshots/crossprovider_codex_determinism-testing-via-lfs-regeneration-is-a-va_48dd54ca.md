---
name: crossprovider codex determinism-testing-via-lfs-regeneration-is-a-va
description: Determinism testing via LFS regeneration is a valid batch-data verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, git-lfs, determinism, corpus]
---

For Git-LFS-fetched content, test determinism by re-running the fetch/extract pipeline and verifying byte-identical regeneration: if `git status --porcelain` on the extracted artifacts is empty after a fresh fetch, the pipeline is deterministic and faithful to the fetched binaries. This is critical for corpus/batch validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
