---
name: session-end
description: >
  Session close checklist — ensures all work is properly documented, archived,
  or forwarded before clearing context. Run before every /clear or end of session.
version: 1.0.0
updated: 2026-02-19
category: workspace-hub
triggers:
  - end session
  - close session
  - before clear
  - session wrap up
  - wrap up
  - finish session
related_skills:
  - workspace-hub/save
  - workspace-hub/improve
  - workspace-hub/session-start
capabilities:
  - session-close-checklist
  - work-item-update
  - learning-capture
requires: []
invoke: session-end
---
# Session End Skill

Run before every `/clear` or end of session. Ensures no work is lost and
the queue reflects actual session progress.

## When to Use

- Before running `/clear`
- At the end of a productive session
- Before switching machines

## Checklist (Claude walks through each)

### 1. Open working/ items

Check `.claude/work-queue/working/`. For each item:
- Update `percent_complete` to reflect actual progress
- Add session notes to the item body if significant discoveries were made
- If done: move to archive gate (Step 4)
- If blocked: move to `blocked/`, update `blocked_by`

### 2. Completed items — archive gate

For each item to archive, verify ALL conditions:
- [ ] `status: done`
- [ ] `percent_complete: 100`
- [ ] `plan_reviewed: true` AND `plan_approved: true`
- [ ] Any partial work has a follow-up WRK item created and linked via `followup: [WRK-YYY]`
- [ ] Ecosystem scan complete: does completing this item reveal new work? If yes, create new WRK items first
- Archive only when all conditions met

### 3. New items discovered this session

Capture any ad-hoc discoveries, user requests, or follow-ups that weren't
formalized as WRK items. Create them now in `pending/` with appropriate priority.

### 4. Learning capture

Run `/improve --dry-run` (optional) to preview what learnings would be captured.
Or simply note key lessons in `.claude/memory/` topic files directly.

### 5. Snapshot + clear

Run `/save` to capture session state. Then `/clear` is safe.

## Archive Gate (detail)

No item is archiveable unless:
1. `status: done` + `percent_complete: 100`
2. `plan_reviewed: true` + `plan_approved: true` (ALL routes)
3. Partial work -> follow-up WRK item created + `followup: [WRK-YYY]` in frontmatter
4. Ecosystem scan done: linked items checked for new opportunities
5. `followup:` list in frontmatter if any new items were spawned
