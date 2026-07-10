> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-09
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gh_always_refresh.md

---
name: Always refresh from GitHub
description: Never use cached GH issue data — always fetch fresh because work may have progressed between queries
type: feedback
---

Always fetch fresh data from GitHub for every query about issues/work items. Never reuse results from earlier in the conversation.

**Why:** The user executes work between queries, so issue state (labels, stage, acceptance criteria) changes frequently. Stale data leads to wrong recommendations.

**How to apply:** Every time the user asks about GH issues, run `gh issue list` / `gh issue view` again — even if the same issues were fetched minutes ago.
