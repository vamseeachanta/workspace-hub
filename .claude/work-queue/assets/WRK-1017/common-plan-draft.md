# WRK-1017 Common Plan Draft

Use this document as the shared starting point for `claude`, `codex`, and
`gemini` Stage 5 planning passes.

Rules:
- Preserve the section headings exactly in each model-specific plan.
- Start from this draft; extend it, do not replace it with a new structure.
- Keep Route B authority with the inline `## Plan` in `WRK-1017.md`.
- Treat model-specific plan files as evidence inputs for the combine step.
- For each model pass, use model-specific high-effort wording rather than the
  exact same phrase for all three models.
- Keep one shared intent across all model passes: prioritize planning quality
  over speed, challenge assumptions, compare alternatives, identify failure
  modes, and seek the best plan rather than the fastest completion.

## Summary
- WRK: `WRK-1017`
- Problem: agents are skipping Stage 5 interactive plan review and moving ahead
  without the required agent-user planning session.
- Goal: make Stage 5 harder to skip and easier to verify across the workflow
  contract.
- Route: `B`
- Canonical execution plan location: inline `## Plan` in `WRK-1017.md`

## Problem Frame
- Stage 5 is defined as an interactive agent-user planning session, not a
  one-way HTML drop.
- Current failure mode: agents move from Stage 4 plan creation to Stage 6
  cross-review or Stage 7 without completing the planning dialog, decision
  capture, and evidence logging.
- The fix must make the blocking nature of Stage 5 explicit in both prose and
  evidence expectations.

## In-Scope Files
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`

## Required Stage 5 Substeps
- Create one common draft to seed all planning passes.
- Seek user review and approval on the common draft plan in a live
  user-interactive review session before launching the model-specific planning
  passes.
- Review wording rule:
  - this is a human-in-the-loop review checkpoint
  - this review is manual and user-interactive
  - do not automate the review conversation
  - do not auto-capture approval
  - do not auto-advance the workflow after review
- In Claude CLI:
  - independent `claude` plan pass using synthesis-heavy effort wording and
    explicit quality-over-speed instruction
  - document and prepare to exit with mandatory session-log/evidence update
- In Codex CLI:
  - independent `codex` plan pass using execution-heavy effort wording and
    explicit quality-over-speed instruction
  - document and prepare to exit with mandatory session-log/evidence update
- In Gemini CLI:
  - independent `gemini` plan pass using exploration-heavy effort wording and
    explicit quality-over-speed instruction
  - document and prepare to exit with mandatory session-log/evidence update
- Combine the individual plans into one synthesized plan using the orchestrator
  agent.
- Rate each model plan during the combine step.
- Seek user review and approval on the combined plan in a live
  user-interactive review session.
- Review wording rule:
  - this is a human-in-the-loop review checkpoint
  - this review is manual and user-interactive
  - do not automate the review conversation
  - do not auto-capture approval
  - do not auto-advance to Stage 6 after review

## Required Artifacts
- `.claude/work-queue/assets/WRK-1017/common-plan-draft.md`
- `.claude/work-queue/assets/WRK-1017/claude-plan.md`
- `.claude/work-queue/assets/WRK-1017/codex-plan.md`
- `.claude/work-queue/assets/WRK-1017/gemini-plan.md`
- `.claude/work-queue/assets/WRK-1017/combined-plan.md`
- `.claude/work-queue/assets/WRK-1017/evidence/user-review-plan-draft.yaml`

## Required Contract Changes
- Make Stage 5 visibly blocking in the workflow contract text.
- Express Stage 5 as ordered planning-and-synthesis substeps.
- Require saved artifacts for each model-specific planning pass.
- Require a mandatory session-log/evidence update after each model pass.
- Preserve browser-open and origin-publish requirements.
- Preserve the `user-review-plan-draft.yaml` evidence requirement.
- Preserve explicit user response as a prerequisite for Stage 6.

## HTML and Review Requirements
- The plan-review HTML must include `Plan Quality Eval Comparison`.
- The compare section must show:
  - `claude`, `codex`, and `gemini` plan ratings
  - the combine-step decision
  - why key elements were kept or rejected
- The user review must include the HTML `Gate-Pass Stage Status` section.

## Verification Targets
- Verify all three workflow contract files reflect the same Stage 5 ordering.
- Verify each model pass requires a saved handoff note plus session-log/evidence
  update.
- Verify the plan-review HTML renders `Plan Quality Eval Comparison`.
- Verify the gate text still blocks Stage 6 until user review is completed.
- Verify no Stage 5 checklist requirement is removed while adding the new
  substeps.

## Quality Evaluation Rubric
- Overall rating scale: `strong | adequate | weak`
- Required dimensions:
  - completeness
  - test-eval quality
  - execution clarity
  - risk coverage
  - standards/gate alignment

## Risks and Failure Modes
- Contract drift across the three workflow files.
- Weak wording that still allows agents to interpret Stage 5 as optional.
- A model-specific plan that changes structure and makes synthesis harder.
- Loss of existing gate requirements while adding new substeps.
- Treating saved model plans as the canonical execution plan instead of evidence
  inputs.

## Decisions Already Fixed
- Update all three workflow contract files in the same WRK.
- Keep Route B inline `## Plan` authoritative.
- Use `strong | adequate | weak` for overall plan quality.
- Require mandatory session-log/evidence updates after each model pass.
- Use `claude`, then `codex`, then `gemini` ordering.
- Use model-specific effort wording rather than assuming `deep think` /
  `ultra think` are interpreted identically by all models.
- Keep user review explicit at two points: common draft approval and combined
  plan approval.

## Combine-Step Expectations
- Produce one synthesized plan in `combined-plan.md`.
- Rate each model-specific plan using the common rubric.
- Record why each retained, merged, or rejected element was chosen.
- Normalize the approved combined plan back into `WRK-1017.md` inline `## Plan`.

## Open Questions For Model Planning
- What exact wording best prevents agents from skipping Stage 5?
- Where should the substep list live in each of the three workflow contracts?
- What is the minimal additional wording needed to avoid redundant or conflicting
  gate language?
- What verification commands best prove the new requirements without adding new
  tooling?
- Should the Stage 5 automation live in a new orchestrator-facing script or as
  an extension of `scripts/agents/plan.sh`?
