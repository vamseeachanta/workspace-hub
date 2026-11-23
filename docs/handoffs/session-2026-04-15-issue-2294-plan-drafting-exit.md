# Exit Handoff — #2294 plan drafting and partial review state

Date: 2026-04-15
Issue: #2294 — `chore(skills): salvage #2290 follow-on learnings for regression coverage and github-code-review scope`

## What was completed

1. Created the canonical plan artifact:
   - `docs/plans/2026-04-15-issue-2294-salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope.md`
2. Added the plan index row to:
   - `docs/plans/README.md`
3. Posted GitHub planning updates to #2294:
   - planning started
   - resource-intelligence summary
   - draft-plan-created update
4. Ran an initial adversarial review wave and captured artifacts:
   - `scripts/review/results/2026-04-15-plan-2294-claude.md`
   - `scripts/review/results/2026-04-15-plan-2294-codex.md`
   - `scripts/review/results/2026-04-15-plan-2294-gemini.md`
5. Revised the draft plan based on review findings:
   - made preserved-branch retrieval explicit via `git show`
   - removed the optional neighboring-skill update backdoor
   - added explicit allowlist + self/historical exclusions for deleted-path scans
   - added unconditional TDD items for scope-boundary and self-exclusion checks
   - tightened acceptance criteria around no edits to `github-auth` / `github-pr-workflow`

## Current truth state

- Plan file exists locally and is indexed.
- The plan has been revised after initial review findings.
- A clean post-revision re-review was NOT completed before exit.
- Therefore the issue is NOT ready for `status:plan-review` yet.
- `docs/plans/README.md` status for #2294 remains `draft`.
- No implementation work was started.

## Review artifact state

### Claude
- Verdict: MINOR
- Main findings:
  - all TDD tests were conditional in the earlier draft
  - two open questions were actually design decisions that needed resolution up front
  - optional neighboring-skill update path was scope creep
  - deleted-path scans risked self-referential false positives
- Artifact:
  - `scripts/review/results/2026-04-15-plan-2294-claude.md`

### Codex
- Verdict: MAJOR, but primarily because retrieval adequacy was insufficient in the initial run
- Main useful residual findings:
  - protect semantic preservation of `github-code-review`
  - preserve `references/review-output-template.md`
  - do not drift into `github-auth` / `github-pr-workflow`
- Artifact restored from the successful initial review output after a later failed rerun attempt temporarily truncated the file:
  - `scripts/review/results/2026-04-15-plan-2294-codex.md`

### Gemini
- Verdict: APPROVE on the earlier draft, with useful non-blocking findings
- Main useful findings:
  - make branch retrieval explicit
  - avoid deleted-path false positives on historical/test files
  - remove neighboring-skill optional-update backdoor
- Artifact restored from the successful initial review output after a later interrupted rerun attempt temporarily truncated the file:
  - `scripts/review/results/2026-04-15-plan-2294-gemini.md`

## Important caveat

A follow-up rerun attempt from `/tmp` to force stdin-only review did NOT complete cleanly:
- Codex refused because the directory was not trusted
- Gemini was interrupted while scanning `/tmp`
- Claude rerun was skipped when the user asked to prepare for exit

Because of that, the canonical state is:
- initial review wave findings are documented
- the plan is revised accordingly
- clean re-review is still pending

## Recommended next action on resume

1. Re-run adversarial review on the REVISED plan using a review package that does not depend on uncommitted repo-state discovery.
2. Prefer a file/bundle-based prompt that includes the full revised plan text inline.
3. If all providers return APPROVE/MINOR, update the plan’s review summary accordingly.
4. Post a GitHub review-synthesis comment.
5. Move #2294 to `status:plan-review`.
6. Stop and wait for user approval.

## Files to inspect first on resume

- `docs/plans/2026-04-15-issue-2294-salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope.md`
- `docs/plans/README.md`
- `scripts/review/results/2026-04-15-plan-2294-claude.md`
- `scripts/review/results/2026-04-15-plan-2294-codex.md`
- `scripts/review/results/2026-04-15-plan-2294-gemini.md`

## Explicit non-actions taken

- Did NOT set `status:plan-review`
- Did NOT post the final plan for approval
- Did NOT create `.planning/plan-approved/2294.md`
- Did NOT start implementation
