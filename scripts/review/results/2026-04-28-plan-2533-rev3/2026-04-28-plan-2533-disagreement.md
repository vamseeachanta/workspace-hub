# Disagreement report — plan #2533 (2026-04-28)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- Plan weakens a live issue acceptance criterion from required to optional. GitHub issue `#2533` says “Use `docs/BUSINESS_BRAIN.md` and live immediate-child git repos as the starting inventory” and its acceptance criteria require “Every immediate-child local git repo not listed in `docs/BUSINESS_BRAIN.md` is either added, explicitly excluded, or marked as inventory drift.” Plan §Pseudocode says to “optionally enumerate local immediate-child git repos,” and §Acceptance Criteria only requires source membership from `BUSINESS_BRAIN`, overview, and “optional local inventory snapshot.” That can pass without satisfying the issue’s explicit local-repo inventory requirement.
- Plan’s evidence validation is not deterministic for cross-repo mission sources. Plan §Pseudocode `derive_repo_mission(repo)` uses per-repo `AGENTS.md`, `README.md`, and `docs/README.md`; §Acceptance Criteria requires exact source paths and path validation. But most repos named in `docs/BUSINESS_BRAIN.md` and `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` are sibling/external repos, not files in the `workspace-hub` Git checkout. Plan §validate_artifact only allows “path exists in the repo checkout” or “external/legacy with rationale,” which means CI either fails on valid sibling-repo evidence or accepts unverified external evidence. The plan lacks a deterministic source snapshot, URL/hash, or committed evidence manifest for those repo-local mission claims.
- Review artifact binding is stale/ambiguous. Plan header §Review artifacts points to `scripts/review/results/2026-04-28-plan-2533-codex.md`, `gemini.md`, and `disagreement.md`, but those artifacts are for the prior failed review wave: the Codex artifact still contains MAJOR blockers that rev-3 claims to fix, and the disagreement artifact says “Rev-2 requires rerun before #2533 can move to `status:plan-review`.” Plan §Adversarial Review Summary says “rev-3 addresses Codex rev-2 blockers and should be rerun,” but the artifact map still presents stale artifacts as the review artifacts for this plan. That risks governance treating old review evidence as current rev-3 approval evidence.

### gemini

- Plan §Files to Change instructs to "Verify/update the existing #2533 plan-index row status only; do not duplicate the row" and §TDD Test List `test_plan_index_has_single_2533_row` asserts "Implementation does not duplicate the already-created plan-index row". However, `docs/plans/README.md` contains zero matches for `2533` at HEAD. The premise is false; if implementation attempts to update an existing row, it will fail or do nothing.
- Plan §Evidence (embedded verification) claims that issues `#2461`, `#2463`, `#2464`, and `#2465` are `CLOSED` and should be used as "already-completed evidence". However, the `docs/plans/README.md` index lists `#2461` and `#2463` as `draft`, and `#2464` and `#2465` as `plan-approved`. None of them are closed or completed at HEAD, making the claim of "already-completed evidence" false and risky to rely upon.

