# Interrupted Approved-Issue Execution Handoff

Use this reference when an approved GitHub issue execution run is interrupted by context compaction, tool-call budget limits, user stop, or a shift to meta-work before implementation/closeout is complete.

## Trigger

- Issue is already `status:plan-approved` or otherwise approved for execution.
- Work has started, but the run stops before one or more closeout gates: GREEN tests, broader validation, adversarial review, commit/push, GitHub evidence comment, label update, or close.
- Especially common after a RED TDD run where tests are written and failing but implementation has not started.

## Required final/handoff shape

Do **not** use completion language. Report the work as in-progress and blocked/interrupted.

Include:

1. **Current state**
   - Issue number/title/state/labels if known.
   - Worktree/branch if known.
   - Gate reached: e.g. `RED/TDD`, `implementation started`, `validation pending`.

2. **Evidence**
   - Exact tests/validators run and their result.
   - Exact dirty/untracked paths observed.
   - Files modified intentionally vs suspicious/session residue.
   - Plan/contract paths inspected.

3. **Gap/blocker**
   - First unmet acceptance criterion.
   - Any missing artifact/script/config/report.
   - Explicit statement that validation, review, commit/push, and closeout are not done when true.

4. **Recommended resumption sequence**
   - Re-check live issue labels/state.
   - Re-check `git status` and diffs.
   - Re-run the targeted failing tests/validators; do not rely solely on the prior narrative.
   - Continue RED → GREEN → refactor → targeted validation → adversarial review → commit/push → GitHub closeout.

## RED-state wording pattern

Use wording like:

> Status: execution is in RED/TDD stage, not complete.
> Failing tests are valid progress, but no implementation/validation/closeout has landed yet.

Avoid wording like:

> Completed the issue.
> Ready to close.
> Implemented normalization.

unless the corresponding validation, commit/push, GitHub evidence, and closeout gates are complete.

## Suspicious residue handling

If a dirty file is unrelated to the approved scope, identify it as suspicious/session residue and make the next action explicit:

- revert it if proven unrelated;
- preserve it only if a live diff/plan/issue proves it belongs to the approved work;
- never silently commit broad dirty state during interruption recovery.

## Resume guardrail

On resume, treat this handoff as a lead, not authority. Live state wins over handoff text. Re-verify with issue state, filesystem state, diffs, and tests before editing or closing.