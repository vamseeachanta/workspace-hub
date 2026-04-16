---
name: evaluate-local-commits-via-cherry-pick-dry-run
description: Technique to identify which ahead commits contain real changes vs. already-merged or ephemeral content
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["git", "workflow", "commit-analysis"]
---

# Evaluate Local-Only Commits via Cherry-Pick Dry-Run

When you have ahead commits on a local branch relative to origin, use `git cherry-pick --dry-run` against each commit to classify them: exit 0 with no changes = already in origin; exit 0 with staged changes = real delta; conflicts = real delta needing sequencing. This lets you quickly filter ephemeral commits (like daily regenerations or auto-syncs) from substantive changes worth preserving or upstreaming.

## Follow-on triage when upstream already landed similar work

If the dry-run or a real cherry-pick attempt shows the work is already effectively upstream:

1. Do not assume the local branch is worthless or safe to cherry-pick wholesale.
2. Preserve the branch as forensic/reference evidence until compared.
3. Compare only the high-signal files against `origin/main`, for example:
   - regression tests
   - canonical skill files touched by the work
   - any review artifacts explaining what changed
4. Separate the local-only delta into:
   - clean, reusable learnings worth salvaging
   - unrelated drift / contamination from the duplicate execution context
5. If the branch contains mixed signal + noise, prefer creating a focused follow-up GitHub issue describing the salvage candidates instead of cherry-picking the whole branch.
6. In that issue, explicitly capture:
   - what landed upstream already
   - what extra local-only checks/content appear useful
   - why direct cherry-pick is unsafe
   - the narrow acceptance criteria for selective salvage

### Example reusable pattern

This was useful when a duplicate implementation branch for an already-landed skills dedup issue contained:
- a stronger regression test with broader dangling-reference surface checks
- a much larger alternate skill draft with possible overlap/noise

The right move was:
- keep upstream as authoritative
- preserve the duplicate branch for reference
- inspect targeted file deltas only
- create a narrow follow-up issue for selective salvage rather than replaying the branch

## Pitfall

A preserved duplicate branch often contains unrelated edits from the worktree/session. Treat it as a source of candidate learnings, not as a merge-ready patch set.