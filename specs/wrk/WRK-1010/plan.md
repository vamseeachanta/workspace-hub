# WRK-1010 Plan — Skill Capability Assessment for WRK-624 Governance Skill Set

**Route:** B (Medium)
**Target repos:** workspace-hub
**Orchestrator:** claude (this session) with codex cross-review

## Phase 0 — Skill Knowledge Map

**Goal:** Build a grounded DAG of the 8 skills before any evaluation.

**Steps:**
1. Read all 8 SKILL.md files (work-queue, workflow-gatepass, wrk-lifecycle-testpack,
   work-queue-workflow, comprehensive-learning, session-start, resource-intelligence,
   cross-review/inline)
2. For each skill extract: triggers, inputs, outputs, handoffs, negative scope
3. Construct flow DAG showing dependency arrows
4. Write `specs/skills/skill-knowledge-map.md` with DAG + per-skill boundary table

**Exit artifact:** `specs/skills/skill-knowledge-map.md`

## Phase 1 — Capability Evaluation (per skill)

For each of the 8 skills:
- Define 3-5 core claimed behaviors from SKILL.md
- Design 1 representative task that exercises those behaviors
- Score: pass (behavior manifests) / partial / fail

Record in scorecard table in `specs/skills/capability-assessment-wrk-624-skills.md`.

## Phase 2 — With vs Without A/B (delta scores)

- For each skill: describe what bare model would produce without skill injection
- Estimate delta score: added value vs bare model (0-5 scale, 0=no added value)
- Identify retirement candidates (delta ≤ 1) and strong-retain (delta ≥ 4)

## Phase 3 — Skill vs Skill Overlap Analysis

Evaluate 4 pairs for overlap:
- `work-queue` vs `work-queue-workflow` — lifecycle routing overlap?
- `workflow-gatepass` vs `wrk-lifecycle-testpack` — gate compliance overlap?
- `session-start` vs `work-queue` — session-init redundancy?
- `comprehensive-learning` vs `workspace-hub:improve` — scope boundary clear?

Score overlap: 0-3 (0=no overlap, 3=full redundancy → merge/retire)

## Phase 4 — Procedural Compliance Eval

For skills with prescribed step sequences (session-start, workflow-gatepass,
work-queue-workflow):
- List required stage order from SKILL.md
- Verify model follows it when skill is injected
- Score: stages-followed / total-required

## Deliverables

| Artifact | Path |
|----------|------|
| Skill knowledge map | `specs/skills/skill-knowledge-map.md` |
| Capability assessment scorecard | `specs/skills/capability-assessment-wrk-624-skills.md` |
| Retirement/merge candidates | Section in assessment doc |
| Follow-up WRK items | Captured via `/work add` |

## Approach Notes

- Phase 0 verifiable: all 8 SKILL.md files read and boundary tables populated
- Capability scores are reproducible by re-reading the SKILL.md claims
- Delta scores are documented reasoning (not automated), but grounded in SKILL.md claims
- At least 1 concrete retirement or merge recommendation required before Stage 12 passes

## Tough Questions

1. **Is a "with vs without" eval feasible without running actual tasks?**
   → For this manual run: yes — we assess based on skill content richness (does it
   add protocol/procedure a bare model wouldn't have?). WRK-1009 will add runtime evals.

2. **What if cross-review skill has no SKILL.md?**
   → Treat inline documentation in work-queue-workflow/SKILL.md as its definition.
   Note the gap as a finding — it should have its own file.

3. **Who maintains the knowledge map going forward?**
   → The map becomes a living doc; comprehensive-learning or a future WRK should
   trigger updates when any SKILL.md changes.

## Tests/Evals

| ID | Test | Method | Pass Condition |
|----|------|--------|----------------|
| T1 | Skill knowledge map completeness | Read all 8 SKILL.md files; verify boundary table has all 5 fields for each | All 8 skills × 5 fields populated in skill-knowledge-map.md |
| T2 | Delta score coverage | Review capability-assessment scorecard | All 8 skills have numeric delta score (0-5) with written rationale |
| T3 | Overlap matrix coverage | Review overlap section | All 4 pairs assessed with overlap score (0-3) |
| T4 | Retirement/merge recommendation | Review assessment doc | ≥1 concrete recommendation with evidence and follow-up WRK captured |
| T5 | Procedural eval completeness | Review procedural section | ≥2 skills with step-sequence have compliance score recorded |

## Acceptance Criteria

- [ ] Phase 0: `specs/skills/skill-knowledge-map.md` produced — DAG + per-skill boundary table
- [ ] All 8 skills assessed across all 4 eval dimensions
- [ ] Per-skill scorecard with delta scores (with vs without)
- [ ] Skill-vs-skill overlap matrix for 4 pairs
- [ ] At least one concrete retirement or merge recommendation with evidence
- [ ] Follow-up WRK items captured for each recommendation
- [ ] Assessment links back to WRK-624 governance review findings
- [ ] Knowledge map updated post-assessment with boundary corrections
