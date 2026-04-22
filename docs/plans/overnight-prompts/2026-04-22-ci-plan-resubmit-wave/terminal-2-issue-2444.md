You are working in `/mnt/local-analysis/workspace-hub` on GitHub issue #2444:
https://github.com/vamseeachanta/workspace-hub/issues/2444

Issue title:
chore(ci-health): aceengineer-admin — add minimal viable CI (uv + ruff + black + pytest) scoped to src/ + tests/

Mission
Revise the canonical plan ONLY. Do not implement `aceengineer-admin` CI. Your goal is to close the latest adversarial-plan blockers and leave the plan ready for a fresh review wave.

Mandatory stance
- Planning-only work. No external repo implementation.
- Do not ask the user questions.
- Do not change approval labels or markers.
- Do not edit any issue other than #2444.

Owned write paths
- `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- optional issue-specific scratch notes under `.planning/quick/2444-*`

Read-only context paths
- `AGENTS.md`
- `docs/plans/README.md` (read-only; DO NOT edit)
- relevant review artifacts under `scripts/review/results/` for 2444
- live #2444 issue comments

Forbidden write paths
- `docs/plans/README.md`
- `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md`
- `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
- `.planning/plan-approved/**`
- any files under external repo `aceengineer-admin/`

Internal workflow
1. Planner
   - Read the latest #2444 plan and recent issue comments.
   - Reconcile live repo facts already embedded in the plan.
2. Reviewer
   - Focus on these known blockers:
     - `uv.lock` / `--frozen` / install-contract inconsistency
     - contradictory CLI import target reasoning
     - leftover TDD-waiver language or other hard-gate conflicts
     - trigger-path inconsistency around `uv.lock`
     - stale claims about approval readiness / review state
3. Implementer
   - Patch only the #2444 plan artifact.
   - Keep the final status conservative unless new real review artifacts were created.
4. Tester
   - Verify by grep/read that:
     - no text still claims this is “no TDD in the strict sense” or equivalent hard-gate waiver
     - trigger-path references are consistent across Deliverable / Acceptance / Detailed Spec
     - the `uv.lock` story is internally consistent
     - the chosen CLI import target is justified consistently everywhere
5. Synthesizer
   - Print short summary:
     - exact sections changed
     - which blocker statements were resolved
     - what still remains before re-review

Specific edits expected
- Eliminate stale contradictory wording left over from older revisions.
- Keep the plan honest about current maturity.
- Make the install path, trigger path, and TDD language fully consistent.
- If the README row is stale, note it in the plan but DO NOT edit `docs/plans/README.md` in this lane.

Validation commands to run
- `grep -n "no TDD\|not in the strict sense\|no unit-test TDD" docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- `grep -n "uv.lock" docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
- `grep -n "aceengineer_admin\.cli\|aceengineer_admin\.automation\.cli" docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`

Output requirements
- Do not commit.
- Do not push.
- Do not change labels.
- Print concise completion summary with remaining blockers.
