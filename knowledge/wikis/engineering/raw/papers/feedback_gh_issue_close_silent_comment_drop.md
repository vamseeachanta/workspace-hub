> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gh_issue_close_silent_comment_drop.md

---
name: gh issue close drops comment if already closed
description: When user closes an issue via gh/UI before the agent runs `gh issue close --comment "..."`, the comment is silently dropped (only a warning prints). Use reopen-comment-close to recover.
type: feedback
originSessionId: b431943f-0498-4574-ae77-b6fc779722da
---
`gh issue close --comment "..."` silently drops the comment when the issue is already in CLOSED state — the CLI emits `! Issue ... is already closed` as a warning and exits 0 without posting the comment.

**Why:** observed 2026-04-17 on assethold #38 + #39. User had closed both via `gh` immediately after saying "verified work"; agent's `gh issue close --comment` ran 4 seconds later, both warnings appeared, both close-summary comments were lost. Recovery required `gh issue reopen NNN` → `gh issue comment NNN --body ...` → `gh issue close NNN` for each.

**How to apply:** When the user signals "verified" or otherwise hints that the issue might already be closed, FIRST check state with `gh issue view NNN --json state` before assuming `gh issue close --comment` will deliver the comment. If state is already CLOSED and a final-state comment matters for audit trail, use the reopen-comment-close sequence explicitly. Don't trust the silent warning to be benign — it represents a lost artifact.
