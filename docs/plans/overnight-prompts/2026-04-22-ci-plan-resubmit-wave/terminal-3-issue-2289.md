You are working in `/mnt/local-analysis/workspace-hub` on GitHub issue #2289:
https://github.com/vamseeachanta/workspace-hub/issues/2289

Issue title:
Plan rollback/recovery for enforcement bypasses detected after commit or push

Mission
Revise the canonical plan ONLY. Do not implement the policy. Your job is to close the latest approval-stage blockers in the plan artifact so it can go back through fresh adversarial review.

Mandatory stance
- Planning-only work.
- Do not ask the user questions.
- Do not change labels, markers, or approval state.
- Do not edit any issue other than #2289.

Owned write paths
- `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
- optional issue-specific scratch under `.planning/quick/2289-*`

Read-only context paths
- `AGENTS.md`
- `docs/plans/README.md` (read-only; DO NOT edit)
- prior #2289 review artifacts in `scripts/review/results/`
- live #2289 issue body/comments

Forbidden write paths
- `docs/plans/README.md`
- `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md`
- `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- `.planning/plan-approved/**`
- `docs/governance/**`
- `scripts/enforcement/**`

Internal workflow
1. Planner
   - Read the canonical #2289 plan and prior review history.
   - Reconcile it against the latest known blockers from the issue thread and review comments.
2. Reviewer
   - Focus on these known blockers:
     - plan still missing or under-specifying required canonical sections / workflow completeness
     - issue asks for rollback-mechanism selection and trigger-policy decision; plan may still read as policy-only advisory without a concrete decision
     - README row missing / plan-review governance drift
     - offline/auth-failure semantics still too loose for approval-grade policy
3. Implementer
   - Patch only the #2289 plan artifact.
   - Keep plan maturity conservative unless real new provider reviews exist.
4. Tester
   - Verify by targeted read/grep that:
     - required plan sections are present and explicit
     - mechanism-selection language is concrete, not evasive
     - the README-row requirement is explicitly acknowledged even though this lane does not edit the README
     - offline/auth-failure policy language is tightened and testable
5. Synthesizer
   - Print a short summary:
     - exact sections changed
     - exact blockers resolved
     - exact blockers still remaining before re-review

Specific edits expected
- Make the plan structurally complete and easier to adversarially review.
- Convert any still-ambiguous “policy-only” wording into a concrete decision contract.
- Do not fake completion of README or provider artifacts; instead make the next re-review path explicit.

Validation commands to run
- `grep -n "README.md\|index row" docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
- `grep -n "offline\|auth failure\|auth_failed\|ls-remote" docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
- `grep -n "advisory boundary\|mechanism\|trigger conditions" docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`

Output requirements
- Do not commit.
- Do not push.
- Do not change labels.
- Print concise completion summary with remaining blockers.
