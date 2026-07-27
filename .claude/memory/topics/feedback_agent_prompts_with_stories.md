> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-27
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_agent_prompts_with_stories.md

---
name: Include agent prompts when creating stories
description: User expects GH stories to come with ready-to-dispatch agent prompts — context, research phase, implementation scope, standards, constraints
type: feedback
---

When creating GH stories/issues, also produce a full agent prompt that can be copy-pasted to dispatch the work.

**Why:** User asked "show these 2 stories with agent prompt" after #466/#467 were created. The prompts let them dispatch work to agents in other terminals without re-explaining context.

**How to apply:** After creating a GH issue, generate an agent prompt block with: working directory, context (existing modules, env paths), research phase (always first), implementation scope (numbered), standards traceability, and "Do NOT" constraints. Format as a fenced code block.
