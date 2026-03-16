---
name: development-workflow-orchestrator-phase-1-user-requirements-read-only
description: 'Sub-skill of development-workflow-orchestrator: Phase 1: User Requirements
  (READ ONLY) (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Phase 1: User Requirements (READ ONLY) (+2)

## Phase 1: User Requirements (READ ONLY)


**File:** `user_prompt.md`

**AI Actions:**
✅ **DO:**
- READ the file thoroughly
- ASK clarifying questions (MANDATORY)
- WAIT for user approval
- UNDERSTAND all requirements completely

❌ **DON'T:**

*See sub-skills for full details.*

## Phase 2: YAML Configuration Generation


**Output:** `config/input/feature-name-YYYYMMDD.yaml`
**Template:** `templates/input_config.yaml`

**AI generates structured configuration:**

```yaml
metadata:
  feature: "csv-data-analysis"
  created: "2026-01-05"
  status: "draft"

*See sub-skills for full details.*

## Phase 3: Pseudocode Review


**Output:** `docs/pseudocode/feature-name.md`
**Template:** `templates/pseudocode.md`

**AI generates implementation plan:**

```markdown
# Pseudocode: CSV Data Analysis Pipeline
