> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gh_issue_comment.md

---
name: Always comment on GitHub issues after implementation
description: Every implemented GitHub issue must get a summary comment via gh issue comment
type: feedback
---

Always post a summary comment on the GitHub issue after completing implementation work.

**Why:** User expects every delivered issue to have a closing/summary comment documenting what was done. This is non-negotiable — "always for every gh issue implemented."

**How to apply:** After finishing work on any `#NNNN` issue, run `gh issue comment <number>` with a structured summary (commit hash, files changed, what was tested). Do this automatically without being asked.
