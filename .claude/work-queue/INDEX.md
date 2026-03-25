<!-- AUTO-GENERATED — do not edit by hand -->
<!-- Generated: 2026-03-25T12:27:38Z by generate-index.py -->

# Work Queue Index

> Auto-generated on 2026-03-25T12:27:38Z. Do not edit manually — run `python .claude/work-queue/scripts/generate-index.py` to regenerate.

## Summary

**Total items:** 46

### By Status

| Status | Count |
|--------|-------|
| pending | 6 |
| archived | 40 |

### By Priority

| Priority | Count |
|----------|-------|
| high | 22 |
| medium | 22 |
| low | 1 |

### By Complexity

| Complexity | Count |
|------------|-------|
| simple | 12 |
| medium | 28 |
| complex | 3 |

### By Category

> Active items only (pending/working/blocked).

| Category | Active Items |
|----------|-------------|
| harness | 1 |
| engineering | 4 |

### By Repository

| Repository | Count |
|------------|-------|
| digitalmodel | 9 |
| workspace-hub | 32 |
| worldenergydata | 3 |

### Plan Tracking

| Metric | Count |
|--------|-------|
| Ensemble planning complete | 0 |
| Plans exist | 19 / 46 |
| Plans cross-reviewed | 14 |
| Plans approved | 21 |
| Brochure pending | 2 |
| Brochure updated/synced | 0 |

## Metrics

### Throughput

| Metric | Value |
|--------|-------|
| Total captured | 46 |
| Total archived | 40 |
| Completion rate | 40/46 (87%) |
| Monthly rate (current month) | 5 archived |
| Monthly rate (prior month) | 10 archived |

### Plan Coverage

| Metric | Count | Percentage |
|--------|-------|------------|
| Pending items with plans | 4 / 6 | 67% |
| Plans cross-reviewed | 0 | 0% |
| Plans user-approved | 0 | 0% |

### Aging

| Bucket | Count | Items |
|--------|-------|-------|
| Pending > 30 days | 0 | - |
| Pending > 14 days | 0 | - |
| Working > 7 days | 0 | - |
| Blocked > 7 days | 0 | - |

### Priority Distribution (active items only)

| Priority | Pending | Working | Blocked |
|----------|---------|---------|---------|
| High     | 1 | 0 | 0 |
| Medium   | 5  | 0  | 0  |
| Low      | 0  | 0  | 0  |

## By Category

> Active items only (pending/working/blocked), grouped by category → subcategory, sorted HIGH→MEDIUM→LOW within each group.

### harness (1 items — 0 high, 1 medium, 0 low)

#### harness / work-queue

| ID | Priority | Title | Status |
|----|----------|-------|--------|
| WRK-5103 | MEDIUM | whats-next.sh should filter out items with no file on disk (ghost entries) | pending |

### engineering (4 items — 0 high, 4 medium, 0 low)

#### engineering / pipeline

| ID | Priority | Title | Status |
|----|----------|-------|--------|
| WRK-5133 | MEDIUM | gmsh parametric mesh convergence study script | pending |
| WRK-5134 | MEDIUM | gmsh OCC boolean workflow for multi-body STEP assemblies | pending |
| WRK-5135 | MEDIUM | gmsh boundary layer field specification — y+ targeting | pending |
| WRK-5136 | MEDIUM | gmsh mesh quality gate script with YAML verdict | pending |

## By Feature

No active feature WRKs found.

## Master Table

| ID | Title | Status | Priority | Complexity | Computer | Plan WS | Exec WS | Provider | Repos | Module | Ensemble? | Plan? | Reviewed? | Approved? | % Done | Brochure | Blocked By |
|-----|-------|--------|----------|------------|----------|---------|---------|----------|-------|--------|-----------|-------|-----------|-----------|--------|----------|------------|
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | - | dev-primary | dev-primary | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | complex | - | dev-primary | dev-primary | codex | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | - | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | - | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | - | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | - | dev-primary | dev-primary | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | archived | high | complex | dev-primary | dev-primary | dev-primary | codex+claude,gemini | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | medium | - | dev-primary | dev-primary | codex | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | high | simple | dev-primary | dev-primary | dev-primary | claude | - | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | medium | - | dev-primary | dev-primary | claude | workspace-hub | work-queue | ❌ | ❌ | ❌ | ❌ | ███ 100% | ⏳ pending | - |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | medium | small | - | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | medium | - | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | medium | low | - | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | medium | - | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | medium | - | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | simple | - | dev-primary | dev-primary | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | medium | - | dev-primary | dev-primary | claude+codex | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | simple | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | █░░ 70% | n/a | - |
| WRK-290 | Install core engineering suite on dev-secondary (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | medium | dev-secondary | dev-secondary | dev-secondary | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-307 | Fix KVM display loss on dev-secondary after switching — EDID emulator or config fix | archived | medium | simple | dev-secondary | dev-secondary | dev-secondary | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | medium | - | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ██░ 90% | ⏳ pending | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | high | simple | dev-primary | dev-primary | dev-primary | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-570 | feat(digitalmodel): port API 579 FFS MATLAB (GML/LML) to Python | archived | high | large | dev-primary | dev-primary | dev-primary | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-1010 | Skill capability assessment for WRK-624 workflow governance skill set | archived | medium | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-1011 | feat(work-queue): workflow-html skill — mandatory consistent HTML review artifact for all WRK items | archived | medium | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ██░ 85% | n/a | - |
| WRK-1029 | Align resource-intelligence skill with Stage 2 micro-skill contract | archived | medium | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-1031 | Single lifecycle HTML: embed full plan content inline, retire snapshot files | archived | high | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ██░ 90% | n/a | - |
| WRK-1039 | Harden gate verifier — 14 gaps from WRK-1035 session audit | archived | high | medium | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | archived | medium | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-1044 |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | archived | high | simple | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | archived | high | simple | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-1244 | Evaluate canonical skill ecosystem quality using skill-creator eval | archived | high | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-1300 | Review and update PDF/document skills — learnings from WRK-1277 and readability sessions | archived | high | medium | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | pending | high | simple | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | - | - | - |
| WRK-1337 | Add subcategory/domain labels to GitHub Issues for WRK items | archived | medium | simple | dev-primary | dev-primary | dev-primary | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-5103 | whats-next.sh should filter out items with no file on disk (ghost entries) | pending | medium | medium | - | - | - | - | - | - | ❌ | ❌ | ❌ | ❌ | - | - | - |
| WRK-5133 | gmsh parametric mesh convergence study script | pending | medium | medium | dev-secondary | dev-secondary | dev-secondary | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | pending | medium | medium | dev-secondary | dev-secondary | dev-secondary | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | pending | medium | medium | dev-secondary | dev-secondary | dev-secondary | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | pending | medium | medium | dev-secondary | dev-secondary | dev-secondary | claude | digitalmodel, workspace-hub | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | archived | high | simple | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-6672 | Machine filtering & display in whats-next | archived | high | medium | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | archived | high | complex | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-6671, WRK-6672 |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | archived | medium | medium | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-6673 |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | archived | medium | simple | dev-primary | dev-primary | dev-primary | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-6671, WRK-6672, WRK-6673, WRK-6674 |

## By Status

### Pending

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | high | simple | workspace-hub | - |
| WRK-5103 | whats-next.sh should filter out items with no file on disk (ghost entries) | medium | medium | - | - |
| WRK-5133 | gmsh parametric mesh convergence study script | medium | medium | digitalmodel | - |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | medium | medium | digitalmodel | - |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | medium | medium | digitalmodel | - |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | medium | medium | digitalmodel, workspace-hub | - |

### Archived

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | medium | medium | worldenergydata | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | high | complex | digitalmodel | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | medium | medium | workspace-hub | - |
| WRK-139 | Develop gmsh skill and documentation | medium | medium | workspace-hub | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | high | medium | workspace-hub | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | medium | simple | digitalmodel | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | high | complex | digitalmodel | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | medium | medium | worldenergydata | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | high | simple | - | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | high | medium | workspace-hub | work-queue |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | medium | small | workspace-hub | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | medium | medium | workspace-hub | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | medium | low | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | high | medium | workspace-hub | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | high | medium | workspace-hub | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | high | medium | workspace-hub | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | low | simple | worldenergydata | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | critical | medium | digitalmodel | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | high | simple | workspace-hub | - |
| WRK-290 | Install core engineering suite on dev-secondary (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | medium | medium | workspace-hub | - |
| WRK-307 | Fix KVM display loss on dev-secondary after switching — EDID emulator or config fix | medium | simple | workspace-hub | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | high | medium | workspace-hub | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | high | simple | - | - |
| WRK-570 | feat(digitalmodel): port API 579 FFS MATLAB (GML/LML) to Python | high | large | digitalmodel | - |
| WRK-1010 | Skill capability assessment for WRK-624 workflow governance skill set | medium | medium | workspace-hub | - |
| WRK-1011 | feat(work-queue): workflow-html skill — mandatory consistent HTML review artifact for all WRK items | medium | medium | workspace-hub | - |
| WRK-1029 | Align resource-intelligence skill with Stage 2 micro-skill contract | medium | medium | workspace-hub | - |
| WRK-1031 | Single lifecycle HTML: embed full plan content inline, retire snapshot files | high | medium | workspace-hub | - |
| WRK-1039 | Harden gate verifier — 14 gaps from WRK-1035 session audit | high | medium | workspace-hub | - |
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | medium | medium | workspace-hub | - |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | high | simple | workspace-hub | - |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | high | simple | workspace-hub | - |
| WRK-1244 | Evaluate canonical skill ecosystem quality using skill-creator eval | high | medium | workspace-hub | - |
| WRK-1300 | Review and update PDF/document skills — learnings from WRK-1277 and readability sessions | high | medium | workspace-hub | - |
| WRK-1337 | Add subcategory/domain labels to GitHub Issues for WRK items | medium | simple | workspace-hub | - |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | high | simple | workspace-hub | - |
| WRK-6672 | Machine filtering & display in whats-next | high | medium | workspace-hub | - |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | high | complex | workspace-hub | - |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | medium | medium | workspace-hub | - |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | medium | simple | workspace-hub | - |

## By Repository

### digitalmodel

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | complex | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | archived | high | complex | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | medium | - |
| WRK-570 | feat(digitalmodel): port API 579 FFS MATLAB (GML/LML) to Python | archived | high | large | - |
| WRK-5133 | gmsh parametric mesh convergence study script | pending | medium | medium | - |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | pending | medium | medium | - |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | pending | medium | medium | - |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | pending | medium | medium | - |

### workspace-hub

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | medium | work-queue |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | medium | small | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | medium | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | medium | low | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | medium | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | medium | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | medium | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | simple | - |
| WRK-290 | Install core engineering suite on dev-secondary (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | medium | - |
| WRK-307 | Fix KVM display loss on dev-secondary after switching — EDID emulator or config fix | archived | medium | simple | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | medium | - |
| WRK-1010 | Skill capability assessment for WRK-624 workflow governance skill set | archived | medium | medium | - |
| WRK-1011 | feat(work-queue): workflow-html skill — mandatory consistent HTML review artifact for all WRK items | archived | medium | medium | - |
| WRK-1029 | Align resource-intelligence skill with Stage 2 micro-skill contract | archived | medium | medium | - |
| WRK-1031 | Single lifecycle HTML: embed full plan content inline, retire snapshot files | archived | high | medium | - |
| WRK-1039 | Harden gate verifier — 14 gaps from WRK-1035 session audit | archived | high | medium | - |
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | archived | medium | medium | - |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | archived | high | simple | - |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | archived | high | simple | - |
| WRK-1244 | Evaluate canonical skill ecosystem quality using skill-creator eval | archived | high | medium | - |
| WRK-1300 | Review and update PDF/document skills — learnings from WRK-1277 and readability sessions | archived | high | medium | - |
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | pending | high | simple | - |
| WRK-1337 | Add subcategory/domain labels to GitHub Issues for WRK items | archived | medium | simple | - |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | pending | medium | medium | - |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | archived | high | simple | - |
| WRK-6672 | Machine filtering & display in whats-next | archived | high | medium | - |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | archived | high | complex | - |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | archived | medium | medium | - |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | archived | medium | simple | - |

### worldenergydata

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | medium | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | simple | - |

## By Priority

### High

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | complex | digitalmodel | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | medium | workspace-hub | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | archived | complex | digitalmodel | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | simple | - | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | medium | workspace-hub | work-queue |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | medium | workspace-hub | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | medium | workspace-hub | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | medium | workspace-hub | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | simple | workspace-hub | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | medium | workspace-hub | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | simple | - | - |
| WRK-570 | feat(digitalmodel): port API 579 FFS MATLAB (GML/LML) to Python | archived | large | digitalmodel | - |
| WRK-1031 | Single lifecycle HTML: embed full plan content inline, retire snapshot files | archived | medium | workspace-hub | - |
| WRK-1039 | Harden gate verifier — 14 gaps from WRK-1035 session audit | archived | medium | workspace-hub | - |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | archived | simple | workspace-hub | - |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | archived | simple | workspace-hub | - |
| WRK-1244 | Evaluate canonical skill ecosystem quality using skill-creator eval | archived | medium | workspace-hub | - |
| WRK-1300 | Review and update PDF/document skills — learnings from WRK-1277 and readability sessions | archived | medium | workspace-hub | - |
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | pending | simple | workspace-hub | - |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | archived | simple | workspace-hub | - |
| WRK-6672 | Machine filtering & display in whats-next | archived | medium | workspace-hub | - |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | archived | complex | workspace-hub | - |

### Medium

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | worldenergydata | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | workspace-hub | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | workspace-hub | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | simple | digitalmodel | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | worldenergydata | - |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | small | workspace-hub | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | workspace-hub | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | low | workspace-hub | - |
| WRK-290 | Install core engineering suite on dev-secondary (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | workspace-hub | - |
| WRK-307 | Fix KVM display loss on dev-secondary after switching — EDID emulator or config fix | archived | simple | workspace-hub | - |
| WRK-1010 | Skill capability assessment for WRK-624 workflow governance skill set | archived | medium | workspace-hub | - |
| WRK-1011 | feat(work-queue): workflow-html skill — mandatory consistent HTML review artifact for all WRK items | archived | medium | workspace-hub | - |
| WRK-1029 | Align resource-intelligence skill with Stage 2 micro-skill contract | archived | medium | workspace-hub | - |
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | archived | medium | workspace-hub | - |
| WRK-1337 | Add subcategory/domain labels to GitHub Issues for WRK items | archived | simple | workspace-hub | - |
| WRK-5103 | whats-next.sh should filter out items with no file on disk (ghost entries) | pending | medium | - | - |
| WRK-5133 | gmsh parametric mesh convergence study script | pending | medium | digitalmodel | - |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | pending | medium | digitalmodel | - |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | pending | medium | digitalmodel | - |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | pending | medium | digitalmodel, workspace-hub | - |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | archived | medium | workspace-hub | - |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | archived | simple | workspace-hub | - |

### Low

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | simple | worldenergydata | - |

## By Complexity

### Simple

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | digitalmodel | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | high | - | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | worldenergydata | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | workspace-hub | - |
| WRK-307 | Fix KVM display loss on dev-secondary after switching — EDID emulator or config fix | archived | medium | workspace-hub | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | high | - | - |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | archived | high | workspace-hub | - |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | archived | high | workspace-hub | - |
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | pending | high | workspace-hub | - |
| WRK-1337 | Add subcategory/domain labels to GitHub Issues for WRK items | archived | medium | workspace-hub | - |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | archived | high | workspace-hub | - |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | archived | medium | workspace-hub | - |

### Medium

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | worldenergydata | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | workspace-hub | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | workspace-hub | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | workspace-hub | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | worldenergydata | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | workspace-hub | work-queue |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | workspace-hub | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | workspace-hub | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | workspace-hub | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | digitalmodel | - |
| WRK-290 | Install core engineering suite on dev-secondary (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | workspace-hub | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | workspace-hub | - |
| WRK-1010 | Skill capability assessment for WRK-624 workflow governance skill set | archived | medium | workspace-hub | - |
| WRK-1011 | feat(work-queue): workflow-html skill — mandatory consistent HTML review artifact for all WRK items | archived | medium | workspace-hub | - |
| WRK-1029 | Align resource-intelligence skill with Stage 2 micro-skill contract | archived | medium | workspace-hub | - |
| WRK-1031 | Single lifecycle HTML: embed full plan content inline, retire snapshot files | archived | high | workspace-hub | - |
| WRK-1039 | Harden gate verifier — 14 gaps from WRK-1035 session audit | archived | high | workspace-hub | - |
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | archived | medium | workspace-hub | - |
| WRK-1244 | Evaluate canonical skill ecosystem quality using skill-creator eval | archived | high | workspace-hub | - |
| WRK-1300 | Review and update PDF/document skills — learnings from WRK-1277 and readability sessions | archived | high | workspace-hub | - |
| WRK-5103 | whats-next.sh should filter out items with no file on disk (ghost entries) | pending | medium | - | - |
| WRK-5133 | gmsh parametric mesh convergence study script | pending | medium | digitalmodel | - |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | pending | medium | digitalmodel | - |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | pending | medium | digitalmodel | - |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | pending | medium | digitalmodel, workspace-hub | - |
| WRK-6672 | Machine filtering & display in whats-next | archived | high | workspace-hub | - |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | archived | medium | workspace-hub | - |

### Complex

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | digitalmodel | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | archived | high | digitalmodel | - |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | archived | high | workspace-hub | - |

## By Computer

### dev-primary (1 active / 23 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | archived | high | complex | digitalmodel |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | high | simple | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | medium | workspace-hub |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | simple | workspace-hub |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | high | simple | - |
| WRK-570 | feat(digitalmodel): port API 579 FFS MATLAB (GML/LML) to Python | archived | high | large | digitalmodel |
| WRK-1010 | Skill capability assessment for WRK-624 workflow governance skill set | archived | medium | medium | workspace-hub |
| WRK-1011 | feat(work-queue): workflow-html skill — mandatory consistent HTML review artifact for all WRK items | archived | medium | medium | workspace-hub |
| WRK-1029 | Align resource-intelligence skill with Stage 2 micro-skill contract | archived | medium | medium | workspace-hub |
| WRK-1031 | Single lifecycle HTML: embed full plan content inline, retire snapshot files | archived | high | medium | workspace-hub |
| WRK-1039 | Harden gate verifier — 14 gaps from WRK-1035 session audit | archived | high | medium | workspace-hub |
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | archived | medium | medium | workspace-hub |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | archived | high | simple | workspace-hub |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | archived | high | simple | workspace-hub |
| WRK-1244 | Evaluate canonical skill ecosystem quality using skill-creator eval | archived | high | medium | workspace-hub |
| WRK-1300 | Review and update PDF/document skills — learnings from WRK-1277 and readability sessions | archived | high | medium | workspace-hub |
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | pending | high | simple | workspace-hub |
| WRK-1337 | Add subcategory/domain labels to GitHub Issues for WRK items | archived | medium | simple | workspace-hub |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | archived | high | simple | workspace-hub |
| WRK-6672 | Machine filtering & display in whats-next | archived | high | medium | workspace-hub |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | archived | high | complex | workspace-hub |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | archived | medium | medium | workspace-hub |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | archived | medium | simple | workspace-hub |

### dev-secondary (4 active / 6 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-290 | Install core engineering suite on dev-secondary (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | medium | workspace-hub |
| WRK-307 | Fix KVM display loss on dev-secondary after switching — EDID emulator or config fix | archived | medium | simple | workspace-hub |
| WRK-5133 | gmsh parametric mesh convergence study script | pending | medium | medium | digitalmodel |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | pending | medium | medium | digitalmodel |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | pending | medium | medium | digitalmodel |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | pending | medium | medium | digitalmodel, workspace-hub |

### (unassigned) (1 active / 17 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | worldenergydata |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | complex | digitalmodel |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | workspace-hub |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | workspace-hub |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | workspace-hub |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | digitalmodel |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | medium | worldenergydata |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | medium | workspace-hub |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | medium | small | workspace-hub |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | medium | workspace-hub |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | medium | low | workspace-hub |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | medium | workspace-hub |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | medium | workspace-hub |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | simple | worldenergydata |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | medium | digitalmodel |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | medium | workspace-hub |
| WRK-5103 | whats-next.sh should filter out items with no file on disk (ghost entries) | pending | medium | medium | - |

## Dependencies

| ID | Title | Blocked By | Children | Parent |
|-----|-------|------------|----------|--------|
| WRK-1045 | Session compliance audit — validate 3-agent gate adherence in live sessions after WRK-1035/1044 hardening | WRK-1044 | - | - |
| WRK-1155 | chore(harness): stage-07 P1-findings-resolved checker script | - | - | WRK-1144 |
| WRK-1156 | chore(harness): stage-07/17 gate-passed printer script — emit checkpoint prompt on gate pass | - | - | WRK-1144 |
| WRK-1324 | Fix archive hook deadlock: enforce-stage-machinery blocks evidence writes after all stages complete | - | - | WRK-1316 |
| WRK-5133 | gmsh parametric mesh convergence study script | - | - | WRK-1249 |
| WRK-5134 | gmsh OCC boolean workflow for multi-body STEP assemblies | - | - | WRK-1249 |
| WRK-5135 | gmsh boundary layer field specification — y+ targeting | - | - | WRK-1249 |
| WRK-5136 | gmsh mesh quality gate script with YAML verdict | - | - | WRK-1249 |
| WRK-6671 | Fix stale index & filter bugs in whats-next pipeline | - | - | WRK-6670 |
| WRK-6672 | Machine filtering & display in whats-next | - | - | WRK-6670 |
| WRK-6673 | GH Issues as single source of truth — architecture & sync | WRK-6671, WRK-6672 | - | WRK-6670 |
| WRK-6674 | Retire WRK numbering & renumber to GH issue IDs | WRK-6673 | - | WRK-6670 |
| WRK-6675 | Cross-review /whats-next pipeline end-to-end | WRK-6671, WRK-6672, WRK-6673, WRK-6674 | - | WRK-6670 |

