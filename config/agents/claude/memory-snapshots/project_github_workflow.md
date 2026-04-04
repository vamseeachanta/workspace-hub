---
name: GitHub Issues + Projects for task tracking
description: GitHub Issues are the task tracking system — GSD manages workflow state in .planning/, GitHub tracks work items
type: project
---

GitHub Issues are the task tracking system. GSD framework manages workflow state.

**Why:** 7 test runs of YAML-file-based tracking with enforcement hooks failed — agent consistently bypassed enforcement. GitHub solved it with zero enforcement code.

**How to apply:**
- Project board: https://github.com/users/vamseeachanta/projects/1
- Create issues via `gh issue create`, add to board via `gh project item-add`
- GSD workflow state lives in `.planning/` (STATE.md, ROADMAP.md, phase directories)
- Close via `gh issue close` when complete
- All via `gh` CLI — no UI needed
