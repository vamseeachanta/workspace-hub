# Archived Skill: `github-actions-trigger-and-shell-gotchas`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/github-actions-trigger-and-shell-gotchas`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/github-actions-trigger-and-shell-gotchas`
Consolidation date: 2026-04-29

---

---
name: github-actions-trigger-and-shell-gotchas
description: Prevent false verification gaps in GitHub Actions by checking push path filters, shell compatibility, and shared CI environment failures before concluding a workflow fix worked or failed.
version: 1.1.0
triggers:
  - You changed files expecting a GitHub Actions workflow to run automatically
  - A cross-platform workflow step starts running on Windows after a reorder/refactor
  - CI verification depends on a post-push run, but no run appears
  - A workflow step uses multiline shell syntax and runs on both Linux/macOS and Windows
  - Multiple independent PRs or salvage branches show the same CI failure that may be harness/environment drift rather than branch-specific regressions
  - A PR check fails before reaching the intended validator, e.g. missing `uv`, missing package import after `uv run`, or setup/PYTHONPATH drift
---

# GitHub Actions trigger and shell gotchas

Two recurring CI pitfalls showed up during assethold issue execution (#2448 follow-up after #2442):

## 1. `on.push.paths` can silently suppress the verification run

A valid fix may land on `main` without triggering the workflow you need for proof.
Observed case:
- deleting pathological `.csv` tree entries fixed a Windows checkout blocker
- but `Python Tests` did not auto-run because the workflow only watched:
  - `**/*.py`
  - `requirements*.txt`
  - `pyproject.toml`
  - `uv.toml`
  - `setup.py`
  - `setup.cfg`
  - the workflow file itself
- since the change touched only `.csv` paths, there was no automatic CI run

Operational rule:
1. Before relying on post-push CI evidence, inspect the workflow's `on.push.paths` filters.
2. If your fix does not match those paths, do NOT assume "CI did not run" means the fix failed.
3. Use one of these instead:
   - `gh workflow run <workflow-name> --ref main` when `workflow_dispatch` exists
   - or a deliberate verification commit that touches a watched path
4. In the issue closeout comment, state explicitly that verification used a manual dispatch rather than a push-triggered run.

Recommended command:
```bash
gh workflow run 'Python Tests' --repo OWNER/REPO --ref main
gh run list --repo OWNER/REPO --workflow 'Python Tests' --limit 3
```

## 2. Bash-style multiline `run:` steps can break on Windows PowerShell

Observed case after moving smoke before lint:
```yaml
run: |
  pytest tests/test_smoke.py \
    --verbose \
    --tb=short
```
This worked on Linux/macOS but failed on Windows PowerShell with:
- `Missing expression after unary operator '--'`

Root cause:
- GitHub Actions runs PowerShell by default on Windows
- Bash line continuations (`\`) are not PowerShell syntax
- a step that was previously unreachable can start failing the moment you reorder the workflow to make it reachable

Operational rule:
1. For cross-platform steps, prefer a shell-neutral single-line command when possible:
```yaml
run: pytest tests/test_smoke.py --verbose --tb=short
```
2. Use explicit `shell: bash` only when Bash is intentional and guaranteed on that runner.
3. After reordering workflow steps, re-check shell compatibility on every OS in the matrix, not just the originally failing OS.

## 3. Repeated PR check failures can be shared CI environment drift, not branch regressions

Observed during post-reboot salvage of already-pushed workspace-hub branches:
- two independent PRs from unrelated branches had local targeted validation green and GitHub `Run Tests`/`Code Quality` green
- both failed the same auxiliary checks:
  - `Stage Prompt Drift Guard` failed before real drift analysis with `ModuleNotFoundError: No module named 'workspace_hub'`
  - `Review Evidence Check` failed before review evaluation with `scripts/enforcement/require-review-on-push.sh: line 19: uv: command not found`

Operational rule:
1. When multiple independent PRs show the same failure, inspect check logs before assuming the branch diff is bad:
```bash
gh pr checks <PR> --repo OWNER/REPO --watch=false
gh run view <RUN_ID> --repo OWNER/REPO --job <JOB_ID> --log | tail -120
```
2. Classify whether the failure reached the intended validator or failed during setup/import/tool discovery.
3. If it failed during setup, compare against another independent PR/branch. Identical setup failures across branches are usually CI harness drift.
4. Preserve branch evidence by commenting on the PR with:
   - local validation already run
   - which checks are green
   - exact shared failing checks and first setup error
   - a linked follow-up issue for the CI harness repair
5. Do **not** merge solely because the failure is shared infra; keep the PR parked until required review/merge policy is satisfied or the CI harness issue is repaired.
6. Create a separate planning-required issue for the harness repair instead of absorbing it into an unrelated feature/fix PR.

Common setup-drift signatures:
- `uv: command not found` in a check that invokes a repo script expecting `uv`
- `ModuleNotFoundError` for the repo's own package after an install step, indicating package layout/PYTHONPATH/install-mode mismatch
- post-checkout cleanup warnings from malformed submodule/worktree paths; record them if they may hide future failures, but separate them from the primary setup failure

## 4. Auxiliary tool CLI drift and legacy collection can masquerade as product regressions

Observed during post-reboot PR recovery of an inherited CI branch:
- the intended product/unit fix was already locally green, but the GitHub matrix still failed in surrounding quality steps
- `safety check --json --output safety-report.json` failed because newer Safety versions treat `--output` as a format selector, not a destination file; portable form was `safety check --output json > safety-report.json`
- `bandit` flagged file writes without explicit `encoding`; fixing `open(..., encoding="utf-8")` removed a security-scanner blocker without changing product behavior
- repo-wide `pytest` collection pulled stale legacy modules that failed during import before useful tests ran (missing optional package, missing generated CSVs, import-time execution); for a bounded CI-recovery PR, explicitly ignore those known-retired paths and encode that bounded contract in a verifier script rather than expanding scope into legacy module repair

Operational rule:
1. When a recovery PR is meant to restore CI baseline, classify every remaining failure as one of:
   - target product/test failure
   - auxiliary scanner/tool CLI drift
   - stale legacy test collection/import-time side effect
   - broad quality/coverage debt
2. Fix auxiliary scanner drift narrowly and locally validate the exact command syntax where possible.
3. For stale legacy modules, prefer an explicit `pytest tests/ --ignore=<retired-path> ...` command with comments and a verifier script over silent broad collection, provided the ignored paths are unrelated to the recovery objective.
4. Preserve the distinction in PR/issue comments: "bounded CI contract restored" is not the same as "all legacy modules repaired."
5. If you change workflow command contracts, update any repo-owned workflow verifier in the same commit so future edits do not reintroduce the broad/stale behavior.

## Minimal reusable playbook

When fixing a workflow that should produce a new validation run:
1. Inspect `on.push.paths` before pushing.
2. If your changed files are outside the filter, plan a manual `workflow_dispatch` verification.
3. If you expose a previously unreachable step, inspect its shell syntax across OSes.
4. Prefer shell-neutral one-line commands for matrix jobs unless there is a strong reason not to.
5. If PR checks fail, inspect logs and determine whether the intended validator actually ran.
6. Classify failures that occur outside the intended validator: auxiliary scanner CLI drift, stale legacy test collection, shared setup drift, or true branch regression.
7. Fix scanner/CLI drift narrowly (for example `safety check --output json > report.json`) and use explicit encoding for security-scanner file-write findings.
8. For unrelated stale legacy test modules, use explicit `--ignore` paths plus a verifier-script contract rather than turning a CI-recovery PR into a broad legacy-module repair.
9. If identical setup failures appear across independent PRs, create/link a CI-harness issue and preserve branch evidence in PR comments.
10. Record in the issue comment whether verification came from:
   - push-triggered run
   - manual dispatch run
   - both
   - local targeted validation plus blocked shared CI harness checks

## Why this matters

Without these checks, you can easily misdiagnose:
- "the fix didn't trigger CI" when the workflow filter suppressed the run
- "Windows is still broken" when the original blocker is fixed and a new shell-specific failure is simply the next exposed layer
