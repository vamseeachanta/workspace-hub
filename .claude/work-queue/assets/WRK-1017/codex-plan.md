# WRK-1017 Codex Plan

This plan extends the shared `common-plan-draft.md` structure for the Codex
planning pass.

Rules:
- Preserve the shared section headings so the combine step can compare plans
  directly.
- Keep Route B authority with the inline `## Plan` in `WRK-1017.md`.
- Treat this file as a model-specific evidence input, not the canonical
  execution plan.

## Summary
- WRK: `WRK-1017`
- Problem: agents are skipping Stage 5 interactive plan review and moving ahead
  without the required agent-user planning session.
- Goal: make Stage 5 harder to skip and easier to verify across the workflow
  contract.
- Route: `B`
- Canonical execution plan location: inline `## Plan` in `WRK-1017.md`
- Codex emphasis: make the Stage 5 flow mechanically explicit, reduce ambiguity
  in stage transitions, and preserve verifiable evidence requirements.

## Problem Frame
- Stage 5 is defined as an interactive agent-user planning session, not a
  one-way HTML drop.
- Current failure mode: agents move from Stage 4 plan creation to Stage 6
  cross-review or Stage 7 without completing the planning dialog, decision
  capture, and evidence logging.
- The fix must make the blocking nature of Stage 5 explicit in both prose and
  evidence expectations.
- The likely root cause is not one missing sentence; it is a combination of:
  - Stage 5 being described as a review checkpoint rather than an ordered
    execution sequence
  - insufficient coupling between user interaction requirements and allowed
    stage transitions
  - weak traceability for model-specific planning passes

## In-Scope Files
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`

## Required Stage 5 Substeps
1. Create one common draft to seed all planning passes.
2. Run an independent planning pass with `claude`.
3. Document and prepare to exit with mandatory session-log/evidence update.
4. Run an independent planning pass with `codex`.
5. Document and prepare to exit with mandatory session-log/evidence update.
6. Run an independent planning pass with `gemini`.
7. Document and prepare to exit with mandatory session-log/evidence update.
8. Combine the individual plans into one synthesized plan.
9. Rate each model plan during the combine step.
10. Seek user review and approval on the combined plan.

Codex recommendation for wording:
- use numbered substeps in the Stage 5 contract, not narrative-only bullets
- explicitly state that Stage 6 is unreachable until all Stage 5 substeps are
  complete
- require the combine step to happen before user approval, not after

## Required Artifacts
- `.claude/work-queue/assets/WRK-1017/common-plan-draft.md`
- `.claude/work-queue/assets/WRK-1017/claude-plan.md`
- `.claude/work-queue/assets/WRK-1017/codex-plan.md`
- `.claude/work-queue/assets/WRK-1017/gemini-plan.md`
- `.claude/work-queue/assets/WRK-1017/combined-plan.md`
- `.claude/work-queue/assets/WRK-1017/evidence/user-review-plan-draft.yaml`

Additional Codex recommendation:
- add a saved handoff note artifact for each model pass if not already present in
  session evidence, so the combine step can reconstruct what changed and why

## Required Contract Changes
- Make Stage 5 visibly blocking in the workflow contract text.
- Express Stage 5 as ordered planning-and-synthesis substeps.
- Require saved artifacts for each model-specific planning pass.
- Require a mandatory session-log/evidence update after each model pass.
- Preserve browser-open and origin-publish requirements.
- Preserve the `user-review-plan-draft.yaml` evidence requirement.
- Preserve explicit user response as a prerequisite for Stage 6.

Codex-specific refinements:
- add explicit "do not mark `plan_reviewed: true` during Stage 5" wording where
  the workflow currently risks conflating user approval with cross-review
- mirror the same Stage 5 substep order in all three workflow files to reduce
  contract drift
- preserve the exit checklist after the new substeps so the stronger sequencing
  does not weaken the existing gate

## HTML and Review Requirements
- The plan-review HTML must include `Plan Quality Eval Comparison`.
- The compare section must show:
  - `claude`, `codex`, and `gemini` plan ratings
  - the combine-step decision
  - why key elements were kept or rejected
- The user review must include the HTML `Gate-Pass Stage Status` section.

Codex recommendation:
- render the combine decision as a concise decision summary near the comparison
  table so the user can quickly see what changed between drafts and the final
  synthesis

## Verification Targets
- Verify all three workflow contract files reflect the same Stage 5 ordering.
- Verify each model pass requires a saved handoff note plus session-log/evidence
  update.
- Verify the plan-review HTML renders `Plan Quality Eval Comparison`.
- Verify the gate text still blocks Stage 6 until user review is completed.
- Verify no Stage 5 checklist requirement is removed while adding the new
  substeps.

Codex verification plan:
- run `rg` across the three workflow contract files for Stage 5 wording and the
  ordered substep text
- run `rg` for `user-review-plan-draft.yaml`, `Plan Quality Eval Comparison`,
  `publish evidence`, and `html opened`
- regenerate the relevant plan-draft HTML and verify the section headings render
  in the expected order
- run any existing workflow or skill validation command that already covers these
  files without introducing new tooling

## Quality Evaluation Rubric
- Overall rating scale: `strong | adequate | weak`
- Required dimensions:
  - completeness
  - test-eval quality
  - execution clarity
  - risk coverage
  - standards/gate alignment

Codex self-assessment target:
- prioritize execution clarity and standards/gate alignment, since the main
  defect is lifecycle ambiguity rather than missing technical depth

## Risks and Failure Modes
- Contract drift across the three workflow files.
- Weak wording that still allows agents to interpret Stage 5 as optional.
- A model-specific plan that changes structure and makes synthesis harder.
- Loss of existing gate requirements while adding new substeps.
- Treating saved model plans as the canonical execution plan instead of evidence
  inputs.

Additional Codex risks:
- over-specifying Stage 5 in one file while leaving the others high level
- adding new substeps without clarifying which evidence artifacts prove each one
- creating a combine step that is descriptive but not reviewable by the user

## Decisions Already Fixed
- Update all three workflow contract files in the same WRK.
- Keep Route B inline `## Plan` authoritative.
- Use `strong | adequate | weak` for overall plan quality.
- Require mandatory session-log/evidence updates after each model pass.
- Use `claude`, then `codex`, then `gemini` ordering.

Codex planning stance:
- prefer minimal but unambiguous contract text
- strengthen stage transitions and checklist wording instead of adding a large
  amount of explanatory prose

## Combine-Step Expectations
- Produce one synthesized plan in `combined-plan.md`.
- Rate each model-specific plan using the common rubric.
- Record why each retained, merged, or rejected element was chosen.
- Normalize the approved combined plan back into `WRK-1017.md` inline `## Plan`.

Codex combine recommendation:
- keep the strongest structural elements from the common draft
- keep the clearest sequencing language from the most executable model plan
- reject any model-specific additions that create new gates or artifacts not
  already justified by the workflow contract

## Open Questions For Model Planning
- What exact wording best prevents agents from skipping Stage 5?
- Where should the substep list live in each of the three workflow contracts?
- What is the minimal additional wording needed to avoid redundant or conflicting
  gate language?
- What verification commands best prove the new requirements without adding new
  tooling?

Codex answers to drive the combine step:
- strongest wording usually combines an explicit stop condition, a numbered
  sequence, and a completion checklist
- the substep list should appear in the Stage 5 contract area of each workflow
  file, not only in supporting commentary
- verification should stay grep-driven plus existing workflow validation, since
  the behavior being fixed is textual contract enforcement

## Handoff Note

Codex planning pass complete. Key additions over the common draft:

1. Root cause framed as lifecycle ambiguity rather than a single missing line.
2. Stage 5 sequencing should be expressed as numbered substeps, not narrative
   prose.
3. Added explicit recommendation to keep `plan_reviewed: true` out of Stage 5.
4. Verification narrowed to grep-based and existing workflow validation checks.
5. Combine-step guidance favors minimal, executable contract wording.

Session-log/evidence update: this file saved at
`.claude/work-queue/assets/WRK-1017/codex-plan.md`. Stage 5 substep 5
(document and prepare to exit) is complete for the Codex pass. Proceed to
substep 8 (combine the individual plans into one synthesized plan).
