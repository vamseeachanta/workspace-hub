# Disagreement report — plan #2626 (2026-05-04)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- Plan path is not a canonical retrievable artifact. The plan header names `docs/plans/2026-05-03-issue-2626-narrow-2552-runbook-fixes.md`, but fetching that path from `main` returns 404 and repo search returns no match. Issue `#2626` comment explicitly says: “Plan file is on disk locally but not yet committed.” This violates the plan’s own AC “Plan committed to `docs/plans/`” and blocks review/tooling from binding to the canonical file.
- The plan omits the required `docs/plans/README.md` index update. `.claude/skills/coordination/issue-planning-mode/SKILL.md` Step 2 says to update the index table in `docs/plans/README.md`, and `docs/plans/_template-issue-plan.md` includes `Update | docs/plans/README.md | add this plan to index`. The plan’s `Files to Change` table does not include `docs/plans/README.md`; issue `#2626` comment admits “Once committed, README index row will be added.”
- Resource Intelligence claims `.planning/plan-approved/2552.md` was found, but fetching `.planning/plan-approved/2552.md` from `main` returns 404. The inline plan’s parent rationale depends on “approval marker noting the deferral rationale”; issue `#2552` does have `status:plan-approved`, but the specific marker cited by the plan is not retrievable in the repository.
- The plan is already marked `plan-review` while its required review artifacts are pending or absent. Header lists `scripts/review/results/2026-05-03-plan-2626-claude.md (pending) | gemini.md (pending)`, and both paths 404 on `main`. `.claude/skills/coordination/issue-planning-mode/SKILL.md` says to keep status conservative as `draft` unless formal review artifacts actually exist, and to only surface after adversarial review is complete.
- Test `t03` is too narrow to prove the scenario-3 contradiction is removed. Issue `#2626` defect 3 cites the problematic guidance as “temporary lift of interaction limit”; plan `t03` only bans a phrase “like `lift the interaction limit`.” A runbook could still contain “temporary lift of interaction limit,” “temporarily disable collaborators_only,” or equivalent guidance and pass the fixed-string test.
- “No regression on the runbook content already approved via #2552” is not implementable as written. Issue `#2552` acceptance requires the runbook to cover “legitimate contributor requests,” while this plan’s pseudocode says to “drop scenario 3 from in-scope” and route non-collaborators to email. The plan provides no regression test or explicit reconciliation showing which #2552 content remains required after dropping scenario 3.

### gemini

- **False File Claim:** Plan §Resource Intelligence Summary claims "Found: `.planning/plan-approved/2552.md` — local approval marker noting the deferral rationale." This file does not exist. A check of `.planning/plan-approved/` confirms no `2552.md` is present. Furthermore, the parent plan `#2552` explicitly states "no `.planning/plan-approved/2552.md` marker created by this lane."
- **Sequencing Contradiction / Impossible File Patch:** Plan §Risks mandates the sequence: "approve+implement #2626 first, then resume #2552 implementation slice with the patched scenario-3". However, Plan §Files to Change instructs modifying `docs/security/external-contributor-runbook.md`. If #2626 is implemented first, this patch will fail because the runbook file does not yet exist; it is designated to be created by the deferred #2552 implementation slice.
- **Resolution Gap:** Plan §Deliverable claims to resolve "the 4 architectural defects from the #2552 Tier-D persistent-MAJOR pattern". However, Plan §Pseudocode only defines 3 resolution steps (1. Revise the proposed test, 2. Define ingestion vector, 3. Resolve scenario-3 contradiction). The 4th defect is silently dropped with no resolution shape provided.
- **Circular Test / Tests the Fixture:** Plan §TDD Test List defines `t04` (`test_runbook_no_pii_hardcoded`) as checking if the "test file contains email addresses or `@username` patterns" via grep. This tests the test fixture itself (`tests/security/test_runbook_external_contributor.py`) rather than asserting the absence of PII in the actual runbook artifact.

