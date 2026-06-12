---
name: crossprovider codex fallback-to-in-repo-equivalents-when-approved-ar
description: Fallback to in-repo equivalents when approved artifact unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [execution, planning, artifact-handling]
---

When a source document referenced in an approved plan is missing from the worktree, use available in-repo proxies (e.g., shards, ledgers) to reconstruct the logical slice. Document the substitution explicitly in the handoff contract so future implementers understand what was used as a proxy and why.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
