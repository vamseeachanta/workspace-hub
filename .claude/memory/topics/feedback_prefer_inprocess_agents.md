> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_prefer_inprocess_agents.md

---
name: Prefer in-process background agents over copy-paste dispatch
description: User prefers Claude running background agents directly rather than generating prompts for manual terminal dispatch
type: feedback
---

When given the choice between "show agent prompts to copy-paste" vs "run them and surface questions", user chose in-process execution. Also prefers lightweight mechanisms (git pre-commit hooks) over token-consuming alternatives (Claude settings hooks) to "keep session actual productive work light weight".

**Why:** User asked "can you run them and surface questions as needed?" on 2026-03-30 when offered 5 dispatch prompts. The /whats-next skill generates prompts, but user wants agents launched directly when possible.

**How to apply:** After /whats-next identifies issues, default to launching background agents rather than just presenting prompts. Use `run_in_background: true` for parallel work. For enforcement mechanisms, prefer zero-token-cost options (shell hooks) over Claude-in-the-loop approaches.
