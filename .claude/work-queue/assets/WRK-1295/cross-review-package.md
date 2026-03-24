# Cross-Review Package: WRK-1295

## WRK Summary
**Title:** Batch LLM summaries — ace_standards + workspace_spec
**Route:** B (Medium) | **Priority:** High | **Parent:** WRK-1245

## Mission
Run Phase B (LLM classification) on ace_standards and workspace_spec documents using
the proven `phase-b-claude-worker.py` pipeline.

## Plan (specs/wrk/WRK-1295/plan.md)

### Execution: 3 phases
1. **Phase A workspace_spec** — Index workspace_spec (currently 0 records, blocker)
2. **Phase B batch** — Launch parallel shards for ace_standards (10) and workspace_spec (4)
3. **Validate** — checkpoint stats, spot-check 20 docs

### Key Facts
- All scripts production-ready (phase-b-claude-worker.py, launch-batch.sh, phase_b_checkpoint.py)
- Pipeline proven on 26K og_standards docs (WRK-1188)
- Resume-safe via SHA-based skip
- Cost: ~$114 at Haiku rates ($0.002/doc × ~57K docs)
- Budget mismatch: WRK says $9, actual ~$114

### Acceptance Criteria
1. workspace_spec Phase A complete (≥716 records)
2. ace_standards Phase B ≥90% classified
3. workspace_spec Phase B ≥90% classified
4. 20 random docs spot-checked
5. Cost within approved budget

## Review Questions
1. Is the plan complete and actionable?
2. Are there missing risks or blockers?
3. Is the cost estimate reasonable?
4. Any concerns about the 3-phase approach?

Respond with: APPROVE or REVISE + P1/P2 findings.
