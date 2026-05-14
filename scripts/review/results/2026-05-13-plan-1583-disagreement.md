# Disagreement report — plan #1583 (2026-05-13)

## Verdicts

| Provider | Verdict |
|---|---|
| codex | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### codex

- Plan artifact claims are not verifiable against `main`. The prompt names `docs/plans/2026-05-13-issue-1583-hermes-config-parity-plan.md`, and the plan’s “Artifact Map” and planning-stage acceptance criteria require that plan file plus a `docs/plans/README.md` row. GitHub fetch for the plan path returned 404, GitHub code search for `1583 hermes config parity docs/plans` returned no results, and the fetched `docs/plans/README.md` visible index did not include `#1583`. This blocks treating the plan as filed/indexed.
- The plan’s approval gate is internally contradictory. “Planning-stage acceptance criteria” requires “at least two adversarial plan review artifacts … with verdict MINOR or better,” but “Adversarial Review Summary” says `Codex | MAJOR`, `Claude | DEFERRED`, and “Overall result: NEEDS RERUN AFTER REVISION.” The same plan also lists review artifact paths in the header, but both `scripts/review/results/2026-05-13-plan-1583-codex.md` and `scripts/review/results/2026-05-13-plan-1583-claude.md` returned 404 on `main`. It cannot be approval-ready under its own criteria.
- The label-cleanup step is risky and under-specified. The plan says stale `status:plan-approved` and `status:working` labels should be removed, but issue `#1583` currently has both labels, and comments show prior implementation work and validation: `Implementation Complete` comment references commit `83b4c4a5`, later comments say repo-side implementation is landed, and the 2026-05-02 blocker recheck calls it an “approved candidate.” The plan does not define how to preserve or supersede the prior approval/implementation state before downgrading the issue to `status:plan-review`.
- The weekly parity test coverage does not prove the new effective-baseline requirement. Plan “Gap 3” and implementation acceptance require weekly parity evidence for config render/merge behavior, `skills.external_dirs`, custom-skills disposition, wiki/knowledge paths, SOUL path, memory snapshot restore/readiness, and sync dry-run output per machine. The TDD list only checks report issue links, secret-file avoidance, and broad pass/unverified classification; it lacks a test that generated report rows actually include those baseline signals. Existing `scripts/cron/weekly-hermes-parity-review.sh` currently reports mainly CLI versions, SSH status, and bridge artifact status, so this is a correctness-critical missing test.

