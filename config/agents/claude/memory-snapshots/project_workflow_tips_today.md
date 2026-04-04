---
name: Workflow tips in /today morning ritual
description: In-progress design for tip-of-the-day feature in /today — hybrid YAML catalog seeded from Boris's 15 features + nightly researcher enrichment
type: project
---

As of 2026-03-29, user approved design direction for a "tip of the day" feature integrated into the `/today` morning ritual.

**Design decisions (approved):**
- Tip surfaces in `/today` morning mode as a new section
- Analyzes recent usage patterns (session signals, git history) to suggest 1-2 underused Claude Code features
- Hybrid catalog approach: static seed YAML + nightly researcher Wednesday `ai-tooling` slot auto-appends new discoveries

**Seed content:** Boris Cherny's 15 hidden/under-utilized Claude Code features (from 2026-03-29 tweet thread):
mobile app, session teleporting, /loop + /schedule, hooks, cowork dispatch, Chrome extension, Desktop web server, fork sessions (/branch), /btw side queries, git worktrees (claude -w), /batch, --bare flag, --add-dir, custom agents (.claude/agents/), voice input

**Integration point:** New section script at `scripts/productivity/sections/workflow-tips.sh` called from `daily_today.sh`, positioned after `research-highlights.sh`.

**Status:** Brainstorming phase — approach (a) selected (tip in /today), catalog approach (c) hybrid selected. Design not yet written as spec.

**Why:** User follows bcherny's Claude Code tips and wants systematic surfacing of impactful but underused features.
