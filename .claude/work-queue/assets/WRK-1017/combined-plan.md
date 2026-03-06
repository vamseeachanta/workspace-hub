# WRK-1017 Combined Plan

This document synthesizes the independent `claude`, `codex`, and `gemini`
planning passes produced from `common-plan-draft.md`.

## Decision Summary

- Use the `claude` plan as the primary structural source.
- Keep `codex` recommendations for stage-transition precision, explicit
  separation of `plan_approved` vs `plan_reviewed`, and lightweight verification.
- Keep `gemini` root-cause framing around plan-mode speed-to-implementation bias
  and artifact-lock progression as supporting rationale.
- Add explicit `deep think` / `ultra think` wording for each independent model
  planning pass, paired with a direct quality-over-speed instruction.
- Reject non-canonical additions that introduce tool-specific or schema-specific
  drift, including:
  - `ask_user` as a mandatory mechanism
  - new YAML status fields such as `approved: true` or `revised: true`
  - a new `Dialogue Log` HTML section for this WRK

## Plan Quality Eval Comparison

| Plan | Overall | Completeness | Test-Eval Quality | Execution Clarity | Risk Coverage | Standards/Gate Alignment | Combine Decision |
|------|---------|--------------|-------------------|-------------------|---------------|--------------------------|------------------|
| Claude | strong | strong | strong | strong | strong | strong | Primary spine |
| Codex | strong | adequate | adequate | strong | adequate | strong | Keep guardrail refinements |
| Gemini | adequate | adequate | adequate | adequate | strong | adequate | Keep selective rationale only |

## Why Elements Were Kept Or Rejected

### Kept from Claude

- Exact hard-gate framing with imperative language.
- Clear recommendation to keep one canonical procedural source and reduce drift.
- Expanded Stage 5 exit checklist with model-plan artifact completion included.
- Concrete grep-based verification commands.

### Kept from Codex

- Explicit recommendation to avoid setting `plan_reviewed: true` during Stage 5.
- Stronger stage-transition language tying Stage 6 eligibility to Stage 5 completion.
- Preference for minimal, executable wording over descriptive prose.

### Kept from Gemini

- Diagnosis that plan-mode behavior creates a speed-to-implementation bias.
- Emphasis that silence must not be treated as approval.
- Concern that artifact presence alone is insufficient without meaningful content.

### Rejected from Gemini

- Requiring `ask_user` as a specific mechanism:
  - Not portable across orchestrators and not part of the canonical contract.
- Requiring new YAML booleans such as `approved: true` or `revised: true`:
  - Conflicts with the existing `approval_decision` pattern already in use.
- Adding a new `Dialogue Log` HTML section in this WRK:
  - Useful idea, but outside the minimal scope needed to fix the Stage 5 skip.

## Synthesized Execution Plan

### Files

- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`

### Change Strategy

Update all three workflow contract files in the same WRK so Stage 5 is enforced
as an ordered, blocking planning-and-synthesis sequence that cannot be skipped by
momentum.

### Contract Decisions To Implement

1. Add or preserve an explicit hard-gate block at the top of Stage 5 in all
   three files using imperative wording:
   - Stage 5 is blocking
   - Stage 6 must not start until Stage 5 is complete
   - presenting HTML alone is insufficient
   - silence is not approval

2. Preserve the same Stage 5 substep ordering across the three workflow
   contracts:
   1. create common draft
   2. `claude` plan with `deep think` / `ultra think` and quality-over-speed instruction
   3. document and prepare to exit
   4. `codex` plan with `deep think` / `ultra think` and quality-over-speed instruction
   5. document and prepare to exit
   6. `gemini` plan with `deep think` / `ultra think` and quality-over-speed instruction
   7. document and prepare to exit
   8. combine plans
   9. rate each plan
   10. user review and approval

3. Keep `work-queue-workflow/SKILL.md` as the most detailed procedural version
   of Stage 5:
   - full 10-substep sequence
   - artifact references
   - explicit checklist
   - explicit STOP/BLOCKING language

4. Update `work-queue/SKILL.md` Stage Contract Stage 5 so it preserves the same
   10-step ordering and checklist semantics while remaining aligned with the
   queue-stage contract.

5. Update `workflow-gatepass/SKILL.md` so its Stage 5 and no-bypass rules
   explicitly block progression unless the Stage 5 sequence and evidence are
   complete, while keeping policy-level wording concise.

6. Require saved artifacts for each model-specific plan:
   - `common-plan-draft.md`
   - `claude-plan.md`
   - `codex-plan.md`
   - `gemini-plan.md`
   - `combined-plan.md`

7. Require each `document and prepare to exit` substep to leave a short handoff
   note plus session-log/evidence traceability.

8. Preserve existing Stage 5 evidence requirements:
   - `user-review-plan-draft.yaml`
   - browser-open evidence
   - origin-publish evidence
   - explicit user response and decision capture

9. Add explicit wording that `plan_reviewed: true` is not a Stage 5 action for
   Route B. User approval and cross-review remain separate gates.

10. Add a planning-effort instruction for all model passes:
   - use `deep think` and `ultra think` wording
   - explicitly ask for the highest-effort planning pass available
   - prioritize best-plan quality over speed
   - stress-test assumptions and compare alternatives before concluding

11. Preserve Route B plan authority:
   - `combined-plan.md` is the saved synthesis artifact for review
   - the authoritative execution plan remains the inline `## Plan` in
     `WRK-1017.md`

## Verification Plan

Use existing commands only.

```bash
# Stage 5 hard-gate wording and artifacts
rg -n "HARD GATE|BLOCKING|user-review-plan-draft.yaml|publish evidence|Gate-Pass Stage Status" \
  .claude/skills/workspace-hub/work-queue-workflow/SKILL.md \
  .claude/skills/workspace-hub/workflow-gatepass/SKILL.md \
  .claude/skills/coordination/workspace/work-queue/SKILL.md

# Ordered Stage 5 substep references
rg -n "common-plan-draft|claude-plan|codex-plan|gemini-plan|combined-plan|document and prepare to exit" \
  .claude/skills/workspace-hub/work-queue-workflow/SKILL.md \
  .claude/skills/workspace-hub/workflow-gatepass/SKILL.md \
  .claude/skills/coordination/workspace/work-queue/SKILL.md

# Route-B gate separation
rg -n "plan_reviewed|plan_approved" \
  .claude/skills/coordination/workspace/work-queue/SKILL.md \
  .claude/skills/workspace-hub/work-queue-workflow/SKILL.md

# Regenerate draft HTML after updates
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-1017 --type plan-draft
```

## Risks To Watch During Implementation

- Duplicating too much Stage 5 prose across files and causing drift later.
- Accidentally weakening existing publish or browser-open requirements.
- Treating the combine artifact as the execution source of truth.
- Adding new fields or tooling that the existing gate system does not recognize.
- Leaving `plan_reviewed` semantics ambiguous.

## Recommended User Review Focus

When this combined plan is presented for the next Stage 5 review, focus on:

1. whether the 10-step Stage 5 ordering is correct
2. whether all three skill files should mirror the same ordering text or use one
   canonical detailed source plus aligned summaries
3. whether the 11-item expanded checklist is the right strictness level
4. whether the combine-step keep/reject decisions match your intent
