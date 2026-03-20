---
id: WRK-NNN
title: "<feature title>"
type: feature
status: pending
priority: high
complexity: complex
created_at: "YYYY-MM-DD"
target_repos: []
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: ""
subcategory: ""
spec_ref: specs/wrk/WRK-NNN/wrk-NNN-<short-name>.md
children: []         # populated by new-feature.sh at Stage 7 exit
plan_reviewed: false
plan_approved: false
percent_complete: 0
---

## Mission

One sentence. Defines the scope boundary — what is IN and what is OUT.

## What / Why

2-3 paragraphs. What problem does this solve and why now.

## Acceptance Criteria

- [ ] AC1
- [ ] AC2

## Decomposition

<!-- REQUIRED for Feature WRKs — filled in at Stage 4b -->
<!-- new-feature.sh reads this section to scaffold child WRKs -->

<!-- wrk_ref: leave blank to create a new WRK; set to existing WRK-NNN to adopt it -->
| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | ... | ... | — | claude | |
| child-b | ... | ... | child-a | codex | WRK-032 |

### Child: child-a

**Files/skills needed (entry_reads):**
- `specs/wrk/WRK-NNN/wrk-NNN-<short-name>.md`
- `.claude/skills/...`

**Acceptance Criteria:**
- [ ] ...

### Child: child-b

**Files/skills needed (entry_reads):**
- ...

**Acceptance Criteria:**
- [ ] ...
