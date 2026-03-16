---
name: skills-curation-phase-1-session-candidate-intake
description: "Sub-skill of skills-curation: Phase 1 \u2014 Session Candidate Intake."
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Phase 1 — Session Candidate Intake

## Phase 1 — Session Candidate Intake


**Purpose**: consume accumulated skill signals from the session analysis pipeline before running graph/research phases.

**Steps:**

1. Read `.claude/state/candidates/skill-candidates.md`
2. For each candidate listed:
   a. Check if a skill already exists at the expected path
   b. If it exists and is current → skip
   c. If it does not exist → classify as shallow or deep gap (see Gap Triage)
   d. If it exists but is stale → flag for online research in Phase 3
3. Clear processed entries from the candidates file (or mark as `processed`)

**Candidate file format expected:**

```markdown
