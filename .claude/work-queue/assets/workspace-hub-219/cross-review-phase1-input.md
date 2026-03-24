# WRK-1029 Phase 1 — Cross-Review Input (Codex)

## Context
Updating `.claude/skills/workspace-hub/resource-intelligence/SKILL.md` v1.0.0 → v1.1.0.
This skill is invoked as a task_agent micro-skill at Stage 2 of every WRK lifecycle.

## Changes in Phase 1 (schema + micro-skill contract)

### 1. Primary exit artifact changed
**Before:** `resource-intelligence-summary.md` (prose markdown)
**After:** `evidence/resource-intelligence.yaml` (machine-readable, gate-checked)

Required schema fields:
- `wrk_id` (string)
- `generated_at` (ISO datetime)
- `generated_by` (string)
- `stage` (integer: 2 or 16)
- `target_repos` (list)
- `domain.problem` (string — REQUIRED, WARN if missing in gatepass)
- `domain.architecture_decision` (string — REQUIRED, WARN if missing in gatepass)
- `existing_files[]` (list of {path, status, notes})
- `skills.core_used[]` (list, min 3 entries)
- `constraints[]` (list)
- `completion_status` (enum: continue_to_planning | pause_and_revise)
- `top_p1_gaps[]` (list — empty = no blockers)

### 2. Micro-Skill Checklist (Stage 2) to be added
1. Read WRK mission from working/WRK-NNN.md
2. Read `category`, `subcategory`, `target_repos` from WRK frontmatter
3. Identify existing infrastructure in `scripts/` + `.claude/skills/`
4. Assess complexity and determine completion_status
5. Write `evidence/resource-intelligence.yaml` with all required fields
6. STOP — do not begin planning or implementation

### 3. Stop guard to cover Stage 2 AND Stage 16
Callout block: "⛔ STOP — Stage 2/16 exit point. Write evidence/resource-intelligence.yaml then halt."

### 4. domain.problem + domain.architecture_decision enforcement
- Required in schema and template
- verify-gate-evidence.py: WARN if missing (not FAIL)
- Follow-up WRK to upgrade to FAIL after 3 production runs

### 5. Version → 1.1.0 + changelog

## Questions for Codex
1. Is the schema complete for gate-evidence verification? Any missing fields that verify-gate-evidence.py would need?
2. Is the 6-item checklist sufficient and correctly ordered? Any gaps?
3. Is WARN (not FAIL) the right gatepass enforcement for domain fields at this stage?
4. Any risks in demoting resource-intelligence-summary.md to optional companion?
5. Does the stop guard wording clearly prevent stage-bleeding for both Stage 2 and 16?
