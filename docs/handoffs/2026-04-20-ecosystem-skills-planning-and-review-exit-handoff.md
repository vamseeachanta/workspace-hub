# Ecosystem skills planning and review exit handoff

Date: 2026-04-20T22:00:00-05:00
Repo: `/mnt/local-analysis/workspace-hub`
Mode: GitHub issue review, issue splitting, plan drafting, adversarial review, CI triage

## Session summary

This session focused on the repo ecosystem skills surface: reviewing existing GitHub issues, identifying gaps in testing/autoresearch coverage, creating follow-up issues, drafting canonical plans, running adversarial review for #2417, and triaging the currently failing PR checks for #2354.

## Work completed

### 1. Existing issue review and gap analysis
Reviewed the current ecosystem-skills/intelligence/testing surfaces, including:
- `#1760` self-improvement command surface
- `#1720` cross-agent corpus audit
- `#2080` skill-test failure umbrella
- `#2089` weekly ecosystem review
- `#2320` skill-usage audit
- `#1879` session-start-routine rebuild

Grounding used during review:
- `uv run pytest tests/skills -q` → 17 failed, 175 passed
- `uv run pytest tests/cron/test_skills_curation.py -q` → 5 passed
- `bash tests/cron/test_skill_autoresearch.sh` → 10 passed, 0 failed
- `scripts/cron/skill-autoresearch-nightly.sh`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `.planning/ROADMAP.md` Phase 999.4 / 999.5

### 2. New GitHub issues created
Created:
- `#2417` — `feat(automation): generalize skill-autoresearch into repo-ecosystem autoresearch runner`
- `#2418` — `feat(automation): add compounding multi-iteration autoresearch with budget guards`
- `#2419` — `fix(tests): reconcile skill markdown contract drift in dark-intelligence/doc-extraction/research-literature/parity tests`
- `#2420` — `fix(skills): restore repo-portfolio-steering balance snapshot contract and threshold behavior`

### 3. Parent/umbrella issue updates
Updated `#2080` twice:
- refreshed the issue with current failing-surface evidence (17 failures, not the older 14 snapshot)
- posted the child-issue split:
  - `#2419` for markdown/content-contract drift
  - `#2420` for executable repo-portfolio-steering behavior

Also updated `#2320` with a grounded state audit comment:
- live issue is `status:plan-approved`
- implementation exists in PR `#2354`
- main branch still lacks the planned files
- current blocker is failing CI / enforcement checks, not plan-review status

### 4. Canonical repo plans drafted
Created canonical plan files:
- `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md`
- `docs/plans/2026-04-20-issue-2419-skill-markdown-contract-drift.md`
- `docs/plans/2026-04-20-issue-2420-repo-portfolio-steering-contract.md`

Updated `docs/plans/README.md` to add rows for:
- `#2417`
- `#2419`
- `#2420`

Also corrected stale local status drift for:
- `#2320` row in `docs/plans/README.md`

### 5. Adversarial review for #2417
Ran multi-provider adversarial review for the current `#2417` draft.

Saved artifacts:
- `scripts/review/results/2026-04-20-plan-2417-claude.md`
- `scripts/review/results/2026-04-20-plan-2417-codex.md`
- `scripts/review/results/2026-04-20-plan-2417-gemini.md`

Net verdicts:
- Claude: MAJOR
- Codex: MAJOR
- Gemini: MAJOR

Convergent blocker pattern:
1. evaluator contract is under-specified
2. results-schema migration / backward compatibility is undecided
3. `workflow-config` lacks a concrete v1 allowlist
4. wrapper/core integration architecture is ambiguous

The `#2417` plan file was updated with the review summary, and a GitHub comment was posted summarizing the wave.

### 6. PR #2354 / #2320 CI triage
Inspected the failing PR checks on `#2354` and posted a grounding comment on the PR.

Root causes found:
1. `Run Tests`
   - `.github/workflows/baseline-check.yml` references shell test files that do not exist in this repo checkout:
     - `scripts/agents/tests/test-task-agents-routing.sh`
     - `scripts/agents/tests/test-plan-gate.sh`
     - `scripts/work-queue/tests/test-user-review-evidence-writers.sh`

2. `Review Evidence Check`
   - `.github/workflows/enforcement-gate.yml` does not install `uv` in the `review-evidence` job
   - but `scripts/enforcement/require-review-on-push.sh` calls `uv run --no-project python ...`
   - observed failure: `uv: command not found`

3. `Stage Prompt Drift Guard`
   - workflow runs `uv`, but import resolution fails in CI:
   - `ModuleNotFoundError: No module named 'workspace_hub'`

Conclusion: PR `#2354` is blocked mainly by cross-cutting workflow/CI drift, not solely by the `#2320` feature logic.

## Current status of the main work items

### #2417
State:
- plan drafted
- adversarial review completed
- NOT approval-ready

Needs a v2 rewrite that explicitly decides:
1. additive vs in-place result artifact strategy
2. concrete evaluator interface + registry + improvement predicate
3. exact `workflow-config` allowlist (or defer that target type)
4. one wrapper/core integration design

### #2419
State:
- child issue created
- canonical plan drafted
- intake comment posted
- no adversarial review run yet

### #2420
State:
- child issue created
- canonical plan drafted
- intake comment posted
- no adversarial review run yet

### #2320 / PR #2354
State:
- live issue is plan-approved
- implementation exists in PR `#2354`
- PR is blocked by failing CI workflow jobs
- local plan index has been updated to reflect this

## Important session artifacts

### Plans
- `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md`
- `docs/plans/2026-04-20-issue-2419-skill-markdown-contract-drift.md`
- `docs/plans/2026-04-20-issue-2420-repo-portfolio-steering-contract.md`

### Review artifacts
- `scripts/review/results/2026-04-20-plan-2417-claude.md`
- `scripts/review/results/2026-04-20-plan-2417-codex.md`
- `scripts/review/results/2026-04-20-plan-2417-gemini.md`

### Scratch / quick-review files created this session
Under `.planning/quick/`:
- `review-2417-plan-prompt.md`
- `review-2417-plan-full.md`
- `review-2417-compact-prompt.md`
- `review-2417-compact-full.md`
- `review-2417-claude-short.md`
- `review-2417-claude.raw`
- `review-2417-codex.raw`
- `review-2417-codex-short.raw`
- `review-2417-gemini.raw`

These are useful for audit/debugging, but are session scratch artifacts.

## Important caution / cleanup note

A shell-quoting mistake during issue-comment posting caused accidental shell interpretation of markdown/file paths, which in turn appears to have created odd untracked path-like artifacts in the repo root. The earlier `git status` showed suspicious untracked entries such as:
- `**Complexity:**`
- `**Date:**`
- `**Issue:**`
- `**Review`
- `**Source`
- `**Status:**`
- `Compatibility`
- `This`

Do NOT assume those are legitimate repo artifacts. They should be inspected and removed deliberately in a cleanup pass before any commit.

## Recommended next actions

### Highest leverage
1. Revise `#2417` plan to v2 using the three-provider MAJOR findings.
2. Decide whether to file dedicated workflow issues for the PR `#2354` CI failures or fix those workflow jobs directly.
3. Run adversarial review for `#2419` and `#2420`.

### Suggested execution order
1. `#2417` v2 rewrite
2. `#2419` / `#2420` review wave
3. CI/workflow blocker resolution for `#2354`
4. Return to `#2320` merge readiness after workflow layer is honest

## Exit status

Session is documented and ready for handoff/exit.
No implementation was started from the newly drafted plans. The main unresolved work is planning/review follow-through and CI/workflow cleanup.