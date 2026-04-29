> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gif_creator_as_proof_pattern.md

---
name: claude-in-chrome gif_creator as audit/skill-authoring/compliance artifact
description: mcp__claude-in-chrome__gif_creator captures up to 50 frames with click indicators; use for audit trail, skill authoring input, and browser-automation compliance evidence
type: feedback
originSessionId: aff40e1f-c80c-4f6d-9797-cba4ecc59a84
---
`mcp__claude-in-chrome__gif_creator` captures up to **50 frames** with click indicators and action labels. Useful as (a) audit trail, (b) input to skill authoring, (c) compliance evidence for browser-automation decisions. Recording lifecycle: `start_recording` → (actions) → `stop_recording` → `export` (with `download=true`).

**Why:** The 2026-04-24 Gmail sweep recorded a 12.9MB GIF capturing the full filter-install + archive sequence. Future sessions can replay the workflow visually without re-running the automation; audit reviewers see exactly what happened frame-by-frame, including which button was clicked and in what order. Cheaper proof than text transcripts, and catches UI drift (e.g., Gmail repositioning a button) that text logs miss.

**How to apply:** At the start of any multi-step claude-in-chrome workflow, call `gif_creator start_recording`. Export to `docs/sessions/YYYY-MM-DD-<purpose>.gif` and commit alongside the session summary markdown. **Max 50 frames**, so:
- Keep sessions focused (one goal per recording).
- Batch similar actions (the creator samples; rapid repeated clicks may compress).
- Split long workflows into multiple recordings with explicit start/stop around each logical phase.

The GIF doubles as the canonical input when promoting the workflow to a persistent skill.
