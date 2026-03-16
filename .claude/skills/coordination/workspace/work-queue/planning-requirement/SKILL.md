---
name: work-queue-planning-requirement
description: 'Sub-skill of work-queue: Planning Requirement.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Planning Requirement

## Planning Requirement


Every WRK item must have an approved plan before implementation begins.

| Route | Plan location | Depth |
|-------|--------------|-------|
| A | `## Plan` inline | 3-5 bullet points |
| B | `## Plan` inline | Steps + test strategy |
| C | `specs/wrk/WRK-NNN/` | Full spec from template |

Plan naming: `wrk-NNN-<short-description>.md` (kebab-case, 3-5 words, NOT random codenames).

Pre-move-to-working gates (hard — never skip):
- `plan_approved: true` — user explicitly approved
- `plan_reviewed: true` — Codex + Gemini verdict received (Route B/C)
- `spec_ref` non-empty (Route C)
- `computer:`, `plan_workstations:`, `execution_workstations:` all set
