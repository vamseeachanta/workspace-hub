# WRK-1017 Gemini Plan

This is the Gemini-specific planning pass for `WRK-1017`, starting from the `common-plan-draft.md`.

Rules:
- Preserve the section headings exactly in each model-specific plan.
- Start from this draft; extend it, do not replace it with a new structure.
- Keep Route B authority with the inline `## Plan` in `WRK-1017.md`.
- Treat model-specific plan files as evidence inputs for the combine step.

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
  cross-review or Stage 7 without completing the planning dialogue, decision
  capture, and evidence logging.
- The fix must make the blocking nature of Stage 5 explicit in both prose and
  evidence expectations. Gemini observes that "Plan Mode" often triggers a
  "speed-to-implementation" bias in LLMs, which must be countered by hard
  interrupts in the skill instructions.

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

## Required Artifacts
- `.claude/work-queue/assets/WRK-1017/common-plan-draft.md`
- `.claude/work-queue/assets/WRK-1017/claude-plan.md`
- `.claude/work-queue/assets/WRK-1017/codex-plan.md`
- `.claude/work-queue/assets/WRK-1017/gemini-plan.md`
- `.claude/work-queue/assets/WRK-1017/combined-plan.md`
- `.claude/work-queue/assets/WRK-1017/evidence/user-review-plan-draft.yaml`

## Required Contract Changes
- **Explicit Blocking Syntax**: Use bold `**BLOCKING**` and `**STOP**` markers in all three skill files.
- **Micro-Checklist Integration**: Embed the 6-item Stage 5 exit checklist directly into the Stage 5 definition in `work-queue.md` and `work-queue-workflow.md`.
- **Artifact-Locked Progression**: Explicitly state that Stage 6 (`cross-review`) tools MUST NOT be called until `user-review-plan-draft.yaml` is present and contains an `approved: true` or `revised: true` status.
- **Dialogue Enforcement**: Instruct agents to use `ask_user` with specific dimensions (scope, criteria, risks) rather than generic "any feedback?" questions.
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
- **Gemini addition**: Add a "Dialogue Log" section to the HTML that summarizes the key points captured in the `user-review-plan-draft.yaml`.

## Verification Targets
- Verify all three workflow contract files reflect the same Stage 5 ordering.
- Verify each model pass requires a saved handoff note plus session-log/evidence
  update.
- Verify the plan-review HTML renders `Plan Quality Eval Comparison`.
- Verify the gate text still blocks Stage 6 until user review is completed.
- Verify no Stage 5 checklist requirement is removed while adding the new
  substeps.
- **Verification Script**: Use `grep` to check for the presence of "BLOCKING" and "STOP" keywords in Stage 5 sections.

## Quality Evaluation Rubric
- Overall rating scale: `strong | adequate | weak`
- Required dimensions:
  - completeness
  - test-eval quality
  - execution clarity
  - risk coverage
  - standards/gate alignment

## Risks and Failure Modes
- **Bypass via Silence**: Agents might interpret user silence as approval if not explicitly forbidden.
- **Fragmented Truth**: If the `combined-plan.md` is not normalized back to `WRK-1017.md`, agents might execute from stale inline plans.
- **Tooling Gap**: If `verify-gate-evidence.py` doesn't strictly check the *content* of the YAML, agents might write empty artifacts to pass the gate.

## Decisions Already Fixed
- Update all three workflow contract files in the same WRK.
- Keep Route B inline `## Plan` authoritative.
- Use `strong | adequate | weak` for overall plan quality.
- Require mandatory session-log/evidence updates after each model pass.
- Use `claude`, then `codex`, then `gemini` ordering.

## Combine-Step Expectations
- Produce one synthesized plan in `combined-plan.md`.
- Rate each model-specific plan using the common rubric.
- Record why each retained, merged, or rejected element was chosen.
- Normalize the approved combined plan back into `WRK-1017.md` inline `## Plan`.

## Open Questions For Model Planning
- **What exact wording best prevents agents from skipping Stage 5?**
  - "STOP — Stage 5 is a BLOCKING interactive gate. Do NOT call `cross-review` (Stage 6) until `user-review-plan-draft.yaml` exists."
  - "This is a DIALOGUE, not a one-way artifact drop."
- **Where should the substep list live in each of the three workflow contracts?**
  - In `work-queue.md` under `## Stage 5 User Review`.
  - In `work-queue-workflow.md` under `## Start-to-Finish Chain`.
  - In `workflow-gatepass.md` under `## No-Bypass Rules`.
- **What is the minimal additional wording needed to avoid redundant or conflicting gate language?**
  - Use "Canonical Stage 5 sequence" and link between files. Ensure `workflow-gatepass` is the "policy" and `work-queue-workflow` is the "procedure".
- **What verification commands best prove the new requirements without adding new tooling?**
  ## Handoff Note

Gemini planning pass complete. Key additions over the common draft:

1. Root cause diagnosed: "Plan Mode" bias triggering speed-to-implementation at the expense of interactive gates.
2. Exact hard gate wording: BOLDFACE **STOP** and **BLOCKING** combined with "Momentum past this point is a workflow violation".
3. Dialogue Enforcement: Explicit instruction to use `ask_user` with mandatory dimensions (scope, criteria, risks).
4. HTML Enhancement: Added "Dialogue Log" section to HTML artifacts to expose the interactive decisions.
5. Minimalist Verification: Grep-based checks for blocking keywords and artifact existence.

Session-log/evidence update: this file saved at
`.claude/work-queue/assets/WRK-1017/gemini-plan.md`. Stage 5 substep 7
(document and prepare to exit) is complete for the Gemini pass. Proceed to
substep 8 (combine the individual plans into one synthesized plan).
