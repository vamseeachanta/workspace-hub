# 2026-04-23 tier-1 indexing contract exit handoff

Timestamp (UTC): 2026-04-23T10:16:37Z
Workspace-hub branch: `integration/runbook-main-compatible`
Workspace-hub HEAD: `2b279a801`

## Session outcome
This session continued the plan-hardening loop for workspace-hub issue `#2460`:
- `#2460` — feat(repo-organization): tier-1 indexing and code-placement contract

The work did NOT reach approval-ready state.
The plan remains local-only and must NOT be posted to GitHub or labeled `status:plan-review` yet.

## Canonical issue and plan
- GitHub issue: https://github.com/vamseeachanta/workspace-hub/issues/2460
- Local plan: `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`

## Current review state
Latest effective local adversarial state recorded in the plan:
- Claude: MAJOR
- Codex: MAJOR
- Gemini: APPROVE
- Overall: FAIL

Do not treat any earlier APPROVE/MINOR artifacts as authoritative unless they match the exact current draft revision.

## What changed in this session
The local #2460 plan was repeatedly hardened to address prior review findings. The main changes now encoded in the plan include:

1. Code-placement scope restored and made explicit.
2. Contract filename strengthened to `TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`.
3. Required routing surfaces broken into individually testable items.
4. Local scorecard treated as local attestation, not canonical branch truth.
5. Universal placement rule reframed as `repo-vs-bulk-artifact-store`.
6. `/mnt/ace/data` demoted to workspace-hub implementation example only.
7. Daily freshness wording strengthened with explicit cadence/refresh language.
8. Negative-authority guard generalized from a dated scorecard file to the scorecard artifact class.
9. BUSINESS_BRAIN added as the authority for the current tier-1 repo set.
10. Checklist field names and allowed values made explicit.
11. TDD sequencing clarified as test-first.
12. Plan now claims the new docs should be brought under the curated stale-reference guard, but review still says this is not strong enough yet.

## Review artifact trail produced during this session
Canonical review summaries:
- `scripts/review/results/2026-04-22-plan-2460-claude.md`
- `scripts/review/results/2026-04-22-plan-2460-codex.md`
- `scripts/review/results/2026-04-22-plan-2460-gemini.md`

Raw provider logs created across the hardening loop:
- `.planning/quick/review-2460-prompt.md`
- `.planning/quick/review-2460-rerun-prompt.md`
- `.planning/quick/review-2460-r3-prompt.md`
- `.planning/quick/review-2460-r4-prompt.md`
- `.planning/quick/review-2460-r5-prompt.md`
- `.planning/quick/review-2460-r6-prompt.md`
- `.planning/quick/review-2460-r7-prompt.md`
- `.planning/quick/review-2460-claude.out`
- `.planning/quick/review-2460-codex.out`
- `.planning/quick/review-2460-gemini.out`
- `.planning/quick/review-2460-r2-claude.out`
- `.planning/quick/review-2460-r2-codex.out`
- `.planning/quick/review-2460-r2-gemini.out`
- `.planning/quick/review-2460-r3-claude.out`
- `.planning/quick/review-2460-r3-codex.out`
- `.planning/quick/review-2460-r3-gemini.out`
- `.planning/quick/review-2460-r4-claude.out`
- `.planning/quick/review-2460-r4-codex.out`
- `.planning/quick/review-2460-r4-gemini.out`
- `.planning/quick/review-2460-r5-claude.out`
- `.planning/quick/review-2460-r5-codex.out`
- `.planning/quick/review-2460-r5-gemini.out`
- `.planning/quick/review-2460-r6-claude.out`
- `.planning/quick/review-2460-r6-codex.out`
- `.planning/quick/review-2460-r6-gemini.out`
- `.planning/quick/review-2460-r7-claude.out`
- `.planning/quick/review-2460-r7-codex.out`
- `.planning/quick/review-2460-r7-gemini.out`

## Latest blockers still preventing GitHub posting
These are the blockers that still matter for the current draft:

1. Stale-reference guard coverage is still not explicit enough
- Reviewers still do not accept that the new docs are unambiguously enrolled in the curated stale-reference guard.
- The plan must make it unmistakable that:
  - `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`
  - `docs/standards/TIER1_INDEXING_CHECKLIST.md`
  are added to `tests/docs/test_banned_stale_references.py` / `STRICT_FILES` as part of the implementation.

2. DATA_PLACEMENT operational rule is still too weakly preserved
- Reviewers still think the plan can degrade the rule into loose prose.
- The plan should require the future contract to either:
  - restate the exact operational thresholds from `docs/standards/DATA_PLACEMENT.md`, or
  - explicitly cite that file as the binding threshold authority.

3. Stale already-done work remains in the plan narrative
- `docs/plans/README.md` already contains the `#2460` row.
- The plan should stop treating this as pending implementation work and instead treat it as an already-satisfied indexed artifact to preserve.

4. Review/state narrative still lags real branch state
- The plan’s review summary is still a moving target and has accumulated historical review waves.
- Before another rerun, reduce ambiguity so the latest local draft state is easier to compare to the latest review artifacts.

## Files currently touched by this session work
Targeted diff currently shows these relevant modified files:
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`
- `docs/plans/README.md`
- `scripts/review/results/2026-04-22-plan-2460-claude.md`
- `scripts/review/results/2026-04-22-plan-2460-codex.md`
- `scripts/review/results/2026-04-22-plan-2460-gemini.md`

## Recommended exact next move
Do NOT post anything to GitHub yet.

Next operator should:
1. patch the local #2460 plan one more time to:
   - explicitly require adding both new docs/standards files to `STRICT_FILES`
   - remove or re-scope stale already-satisfied `docs/plans/README.md` work
   - force the future contract to preserve the exact `10 MB` / `1000 files` rule from `docs/standards/DATA_PLACEMENT.md`
2. refresh the review prompt from the new exact draft
3. run one more three-provider adversarial review wave
4. only if there are no MAJOR findings, then:
   - update canonical review artifacts
   - post the plan to `#2460`
   - add `status:plan-review`

## Resume artifact
Resume from this file:
- `docs/handoffs/2026-04-23-tier1-indexing-contract-exit-handoff.md`
