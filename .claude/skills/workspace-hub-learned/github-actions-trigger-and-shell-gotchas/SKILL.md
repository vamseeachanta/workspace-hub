---
name: github-actions-trigger-and-shell-gotchas
description: Prevent false verification gaps in GitHub Actions by checking push path filters and shell compatibility before concluding a workflow fix worked or failed.
version: 1.0.0
triggers:
  - You changed files expecting a GitHub Actions workflow to run automatically
  - A cross-platform workflow step starts running on Windows after a reorder/refactor
  - CI verification depends on a post-push run, but no run appears
  - A workflow step uses multiline shell syntax and runs on both Linux/macOS and Windows
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

## Minimal reusable playbook

When fixing a workflow that should produce a new validation run:
1. Inspect `on.push.paths` before pushing.
2. If your changed files are outside the filter, plan a manual `workflow_dispatch` verification.
3. If you expose a previously unreachable step, inspect its shell syntax across OSes.
4. Prefer shell-neutral one-line commands for matrix jobs unless there is a strong reason not to.
5. Record in the issue comment whether verification came from:
   - push-triggered run
   - manual dispatch run
   - both

## Why this matters

Without these checks, you can easily misdiagnose:
- "the fix didn't trigger CI" when the workflow filter suppressed the run
- "Windows is still broken" when the original blocker is fixed and a new shell-specific failure is simply the next exposed layer
