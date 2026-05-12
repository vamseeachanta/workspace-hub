> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-12
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_parallel_gh_issue_create_reverses_numbers.md

---
name: Parallel gh issue create reverses numbers
description: When filing multiple GitHub issues via `gh issue create &` in parallel, the API assigns numbers in apparent reverse arrival order — cross-references baked in at creation time will be wrong; apply them only after all issues land.
type: feedback
originSessionId: ec40ba65-385e-48da-98c7-8cf5a6f30e44
---
When filing multiple GitHub issues in a single shell batch with `&` for parallelism, the GitHub API assigns issue numbers in apparent **reverse** arrival order relative to the prompts you wrote.

**Why:** with concurrent POSTs, the request that hits the server last (i.e., the *first* one written in the script, because parallel jobs queue up and the last to finish-spawning is the first to actually fire) gets the lowest number. The behavior was observed concretely 2026-05-06 in `kaggle-rogii-2026`: 8 `gh issue create &` calls produced `#1` for the LAST issue text written in the script (Phase 5), `#8` for the FIRST issue text (Phase 0.5). All 8 cross-references in plans, body text, and labels were off-by-N as a result.

**How to apply:**

1. **Never bake in cross-references at parallel-create time.** Don't write `--body "depends on #2"` in the same shell expansion that creates #2 in parallel — `#2` may not be the issue you think it is.
2. **Two-phase pattern:** create issues first (parallel OK), then in a second pass read their actual numbers (`gh issue list --json number,title --jq ...`) and emit cross-reference comments / label patches.
3. **Sequential creation** (no `&`) preserves the order you write — slower but predictable. Worth the few extra seconds when issue numbers will appear in plans, commits, or commit messages.
4. **Audit immediately:** after a parallel batch, run `gh issue view N --json title --jq .title` for each N and verify titles match the order you intended. A 5-second cross-check saves a 30-minute rename-and-fix-cross-refs-and-restate session like the one that triggered this memory.
5. **The mismatch is silent.** GitHub does not warn you. Plans, comments, and labels may all look reasonable until a downstream agent or human follows a link and lands on the wrong issue.

Recovery cost when missed: rename plan files (`git mv`), update internal cross-refs (1 file × ~5 places typically), edit GH labels, post correction comments, force-restate the affected gates. ~20-30 min for a 1-issue mistake; scales linearly.
