> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_no_reserved_wrk_ids.md

---
name: No local task IDs — use GitHub issues
description: Tasks tracked as GitHub issues, not local ID files or numbering schemes
type: feedback
---

No local task ID systems. Use GitHub issues directly.

**Why:** The old WRK-NNN system with machine-specific ID ranges was unnecessary overhead. GitHub issues are the single source of truth.

**How to apply:** Never create local task numbering. Use `gh issue create` for new tasks. GSD manages workflow state in `.planning/`.
