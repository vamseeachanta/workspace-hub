> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-08
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_cross_repo_closes_at_squash.md

---
name: cross-repo-closes-at-squash
description: Cross-repo `Closes vamseeachanta/workspace-hub#NNNN` keywords fire correctly at squash-merge time, even when batched across 5+ commits in one PR. Verified 2026-05-03.
type: feedback
originSessionId: 20bbbf35-b8fa-4295-a1b2-59fd2252ff45
---
GitHub's auto-close mechanism for cross-repo issue closure works at squash-merge time AND scales to multi-commit batches in one PR.

**Why:** Verified 2026-05-03 with digitalmodel#567 — a single squash-merge of 5 atomic commits, each with `Closes vamseeachanta/workspace-hub#NNNN` in its commit message body, auto-closed all 5 issues at the same instant (20:27:00Z–20:27:01Z timestamps). The squash collapses commit history but preserves message bodies in the squash commit's body, so the keyword scanner sees all 5 references.

**How to apply:**
- For multi-issue fix bundles: write one commit per issue with its own `Closes <ref>` line, then squash-merge. All auto-close.
- For single-issue cross-repo fixes: same pattern with `Closes vamseeachanta/<repo>#NNNN` works (verified earlier 2026-05-03 with digitalmodel#548 → workspace-hub#2603).
- Don't worry about whether the auto-close fires for "the right" commit — at squash-merge it fires for ALL `Closes` references in the squash body.
- Bare `#NNNN` works for same-repo references; cross-repo MUST use `vamseeachanta/<repo>#NNNN` form.

**Memory ref:** validated 2026-05-03 across digitalmodel#548 (1-commit), digitalmodel#567 (5-commit batch), workspace-hub#2620 (1-commit).
