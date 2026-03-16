---
name: skills-curation-execution-checklist
description: 'Sub-skill of skills-curation: Execution Checklist.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


**Pre-run:**
- [ ] `SKILLS_GRAPH.yaml` is readable
- [ ] `.claude/state/candidates/skill-candidates.md` is accessible
- [ ] Active WRK item directories are accessible
- [ ] `curation-log.yaml` is readable (or create stub if missing)

**Phase 1 — Candidates:**
- [ ] Read and parse `skill-candidates.md`
- [ ] Classify each candidate (shallow/deep/already exists)
- [ ] Mark processed entries

**Phase 2 — Graph review:**
- [ ] Load graph and compute demand/depth/gap scores
- [ ] Identify research targets (top 5 by gap score)
- [ ] Identify archival candidates (demand == 0)
- [ ] Log to `skills-graph-review-log.jsonl`

**Phase 3 — Online research:**
- [ ] Run WebSearch for each research target
- [ ] Assess findings (new/update/deprecation)
- [ ] Classify findings as shallow or deep gaps

**Phase 4 — Gap triage:**
- [ ] Auto-create stubs for shallow gaps
- [ ] Spin off WRK items for deep gaps
- [ ] Update category INDEX.md files as needed

**Phase 5 — Health check:**
- [ ] Check all four pipeline health indicators
- [ ] Emit warning summary
- [ ] Append any warnings to `curation-log.yaml`

**Phase 6 — Yield + cadence:**
- [ ] Count yield metrics
- [ ] Evaluate cadence adjustment
- [ ] Write updated `curation-log.yaml`
- [ ] Append run summary to `skills-research-log.jsonl`

---
