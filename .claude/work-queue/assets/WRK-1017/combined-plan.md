# WRK-1017 Combined Plan

This document synthesizes the independent `claude`, `codex`, and `gemini`
planning passes produced from `common-plan-draft.md`.

## Decision Summary

- Use the `claude` plan as the primary structural source.
- Keep `codex` recommendations for stage-transition precision, explicit
  separation of `plan_approved` vs `plan_reviewed`, and lightweight verification.
- Keep `gemini` root-cause framing around plan-mode speed-to-implementation bias
  and artifact-lock progression as supporting rationale.
- Replace one-size-fits-all `deep think` / `ultra think` wording with
  model-specific effort cues, paired with one shared quality-over-speed
  instruction.
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
- Execution-first effort cues fit Codex better than generic reasoning slogans.

### Kept from Gemini

- Diagnosis that plan-mode behavior creates a speed-to-implementation bias.
- Emphasis that silence must not be treated as approval.
- Concern that artifact presence alone is insufficient without meaningful content.
- Exploration-heavy effort cues fit Gemini better than using the exact same
  wording as Claude and Codex.

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
   - create common draft
   - user review and approval on the common draft
   - in Claude CLI:
     - independent `claude` plan pass with synthesis-heavy effort wording and
       quality-over-speed instruction
     - document and prepare to exit
   - in Codex CLI:
     - independent `codex` plan pass with execution-heavy effort wording and
       quality-over-speed instruction
     - document and prepare to exit
   - in Gemini CLI:
     - independent `gemini` plan pass with exploration-heavy effort wording and
       quality-over-speed instruction
     - document and prepare to exit
   - combine plans using the orchestrator agent
   - rate each plan
   - user review and approval

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

10. Add model-specific planning-effort instructions:
   - `claude`: use synthesis-heavy cues such as `deep think`, `ultra think`,
     `challenge assumptions`, and `surface tradeoffs`
   - `codex`: use execution-heavy cues such as `be precise`, `minimize
     ambiguity`, `mechanically verify transitions`, and `prefer the clearest
     executable plan`
   - `gemini`: use exploration-heavy cues such as `consider alternatives`,
     `identify blind spots`, `probe edge cases`, and `seek the most resilient
     plan`
   - keep one shared requirement: prioritize best-plan quality over speed and
     compare alternatives before concluding

11. Preserve Route B plan authority:
   - `combined-plan.md` is the saved synthesis artifact for review
   - the authoritative execution plan remains the inline `## Plan` in
     `WRK-1017.md`

12. Do not automate the Stage 5 review sessions:
   - common-draft review is user-interactive
   - each model planning pass is user-interactive in its own CLI
   - combined-plan review is user-interactive
   - no script should auto-conduct review, auto-capture approval, or auto-open
     Stage 6

Recommended review wording to carry into the plan text:
- `Seek user review and approval in a live user-interactive review session.`
- `This is a human-in-the-loop review checkpoint.`
- `This review is manual and user-interactive; do not automate the review conversation.`
- `Do not auto-capture approval or auto-advance the workflow after review.`

13. Allow assistive tooling only where it reduces operator friction without
    replacing user interaction:
   - prepare prompt/context files
   - print or open the next manual CLI command
   - scaffold evidence files
   - regenerate HTML after manual review steps
   - validate artifact completeness after manual work

14. Validate the manual-review workflow by committing the current work, rerunning
    the appropriate assistive script if introduced, and checking that the review
    process still produces the required artifacts to a good standard using test/eval.

## Manual Interaction Issues

1. Common-draft review evidence is underspecified:
   - the plan now has a real user gate before model passes
   - that gate needs an explicit evidence artifact

2. The boundary between assistance and automation must be explicit:
   - the workflow may help the user navigate terminals and files
   - it must not replace any of the actual review interactions

3. Repeated terminal/context setup is still cumbersome:
   - switching across Claude, Codex, and Gemini manually can create avoidable
     friction and missed evidence steps

4. Rerun validation needs a manual-review-friendly definition:
   - success should mean artifacts and evidence are reproduced correctly after a
     manual pass, not that the system auto-runs the reviews

5. Stage 5 evidence now has two review checkpoints:
   - common draft review
   - combined plan review
   - these must not be conflated

## Suggested Improvements

1. Add a dedicated common-draft review evidence file:
   - recommended: `assets/WRK-1017/evidence/user-review-common-draft.yaml`

2. Keep common-draft review lightweight:
   - use markdown + YAML approval first
   - do not add a second HTML artifact unless it becomes necessary

3. If tooling is added, make it assistive-only:
   - prepare the next CLI command
   - open the relevant artifact path
   - scaffold the next evidence file
   - never run the actual review conversation for the user

4. Keep model-plan files canonical and overwrite in place on rerun:
   - this keeps the manual workflow simple
   - if history is needed later, add snapshots deliberately rather than by default

5. Validate with manual-review-aware tests:
   - artifact existence/content checks
   - evidence presence checks
   - HTML regeneration checks
   - gate-verification checks where applicable

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
- Assuming existing cross-review scripts can be reused even though they are
  wired for implementation review, not Stage 5 planning orchestration.
- Automating too much and accidentally bypassing the two required user review
  checkpoints.
- Failing to define what counts as a successful rerun when validating the new
  planning runner.

## Recommended User Review Focus

When this combined plan is presented for the next Stage 5 review, focus on:

1. whether the 10-step Stage 5 ordering is correct
2. whether all three skill files should mirror the same ordering text or use one
   canonical detailed source plus aligned summaries
3. whether the 11-item expanded checklist is the right strictness level
4. whether the combine-step keep/reject decisions match your intent
