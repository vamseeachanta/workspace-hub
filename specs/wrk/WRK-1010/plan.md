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

## Phase 1 — Capability Evaluation (per skill) — Static/Heuristic

**Scope:** Static analysis of SKILL.md content only (no runtime model execution).

For each of the 8 skills:
- Define 3-5 core claimed behaviors from SKILL.md
- Assess whether the skill provides sufficient protocol/procedure for each behavior
  (i.e., would a model following this skill produce the claimed output?)
- Score: pass (claim is fully specified with verifiable exit conditions) /
         partial (claim present but vague or missing exit artifact) /
         fail (claim made but no procedural guidance given)

Record in scorecard table in `specs/skills/capability-assessment-wrk-624-skills.md`.

## Phase 2 — With vs Without A/B (delta scores)

- For each skill: describe what bare model would produce without skill injection
- Estimate delta score: added value vs bare model (0-5 scale, 0=no added value)
- Identify retirement candidates (delta ≤ 1) and strong-retain (delta ≥ 4)

## Phase 3 — Skill vs Skill Overlap Analysis

**3A — Coarse full-matrix scan (all 8 skills):**
Build an 8×8 overlap matrix at coarse level. For each pair, assess: do they share
triggers, claim the same outputs, or describe the same workflow step?
Score: 0=clearly disjoint, 1=some shared vocabulary, 2=overlapping claims, 3=full redundancy.
Identify top pairs by score for deep-dive.

**3B — Deep review of top-overlap pairs (initially 4):**
- `work-queue` vs `work-queue-workflow` — lifecycle routing overlap?
- `workflow-gatepass` vs `wrk-lifecycle-testpack` — gate compliance overlap?
- `session-start` vs `work-queue` — session-init redundancy?
- `comprehensive-learning` vs `workspace-hub:improve` — scope boundary clear?
(Expand to other high-scoring pairs if 3A reveals new candidates)

Score overlap: 0-3 (0=no overlap, 3=full redundancy → merge/retire)

## Phase 4 — Procedural Completeness Eval — Static/Heuristic

**Scope:** Static analysis only — evaluate documentation quality, not runtime compliance.

For skills with prescribed step sequences (session-start, workflow-gatepass,
work-queue-workflow):
- List required stage order as defined in SKILL.md
- Assess whether each stage has: clear trigger, exit artifact, and blocking condition
- Score: stages-with-complete-spec / total-stages
  (0.0 = none fully specified, 1.0 = all stages have complete spec)
- Note: runtime compliance testing deferred to WRK-1009 (eval framework)

## Deliverables

| Artifact | Path |
|----------|------|
| Skill knowledge map | `specs/skills/skill-knowledge-map.md` |
| Capability assessment scorecard | `specs/skills/capability-assessment-wrk-624-skills.md` |
| Retirement/merge candidates | Section in assessment doc |
| Follow-up WRK items | Captured via `/work add` |

## Approach Notes

- Phase 0 verifiable: all 8 SKILL.md files read and boundary tables populated
- Capability scores cite the exact SKILL.md section supporting the score
- Delta score rubric: 0=no unique protocol, 1=minor terminology aid,
  3=material workflow scaffolding, 5=strong deterministic protocol with artifacts/blockers/handoffs
- Recommendation gate: "at least 1 concrete recommendation" — valid outcomes include
  retain-with-clarification, tighten-boundaries, merge, or retire (no forced retirement)
- Assessment doc per-skill schema: claimed behaviors | SKILL.md citation | score |
  rationale | delta | overlap notes | recommendation

## Tough Questions

1. **Is a "with vs without" eval feasible without running actual tasks?**
   → YES (Gemini MINOR resolved): This entire WRK is static/heuristic analysis of
   SKILL.md content. "With skill" = model has protocol/procedure specified in SKILL.md.
   "Without skill" = bare model has no such protocol. Delta score reflects how much
   procedural guidance the skill adds beyond what a capable model would do naturally.
   Runtime execution tests are out of scope — deferred to WRK-1009.
   Phases 1 and 4 have been updated to be explicit about static-only scope.

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
- [ ] At least one concrete recommendation (retain/refine/merge/retire) with evidence
- [ ] Follow-up WRK items captured for each recommendation
- [ ] Assessment links back to WRK-624 governance review findings
- [ ] Knowledge map updated post-assessment with boundary corrections
