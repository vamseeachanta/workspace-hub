---
name: github-actions-cross-platform-validation-gotchas
description: Execution-time GitHub Actions pitfalls discovered while fixing cross-platform CI workflows — path-filter non-triggers, Windows shell parsing mismatches, and job-scoped validation.
version: 1.0.0
triggers:
  - Executing or debugging a GitHub Actions workflow after a narrow CI fix
  - Cross-platform matrix workflows involving Linux/macOS/Windows runners
  - A push should have triggered CI but no validation run appeared
  - A step works on Linux/macOS but fails only on Windows runners
---

# GitHub Actions cross-platform validation gotchas

Use this when implementing or validating CI fixes in a GitHub Actions workflow, especially matrix jobs across Ubuntu, macOS, and Windows.

## 1. `push.paths` can block the validation run you expected

Observed pattern:
- A real fix lands on `main`
- The workflow does **not** auto-trigger
- The fix touched files outside the workflow's `on.push.paths` filter

Concrete example:
- A workflow watched only `**/*.py`, `pyproject.toml`, `setup.py`, and the workflow YAML
- A fix removed pathological `*.csv` git-tree entries that were breaking Windows checkout
- Because only CSVs changed, no push-triggered validation run happened

Rule:
- Before assuming CI is broken, inspect the workflow's `on.push.paths` filter
- If your fix is outside that filter, use `workflow_dispatch` (or another explicit trigger) for post-change verification

Checklist:
1. Read `.github/workflows/<workflow>.yml`
2. Inspect `on.push.paths`
3. Compare the changed files against the filter
4. If unmatched, manually dispatch the workflow and use that run as the validation artifact

## 2. Windows runners use PowerShell by default

Observed pattern:
- A multiline step written with Bash line continuations works on Ubuntu/macOS
- The same step fails on Windows with a PowerShell parse error such as:
  - `Missing expression after unary operator '--'`

Concrete example:
```yaml
run: |
  pytest tests/test_smoke.py \
    --verbose \
    --tb=short
```

This is valid in Bash, but on Windows PowerShell the continued lines are parsed incorrectly.

Rule:
- For cross-platform steps, do not assume Bash syntax is portable
- Use one of these patterns instead:
  1. single-line command
  2. explicit `shell: bash` where appropriate and available
  3. OS-specific command forms
  4. PowerShell-safe multiline syntax for Windows jobs

## 3. Use job-scoped verification, not whole-run log greps

Observed pattern:
- Aggregated run logs mix output from many matrix jobs
- Grepping the full run log for step names or error strings can produce false positives/false negatives

Rule:
- Prefer `gh run view --json jobs` and inspect the specific matrix leg you care about
- Verify step order and step conclusions from the target job, not from the whole-run text stream

Recommended verification flow:
1. `gh run view <run-id> --json jobs`
2. identify the exact job name (for example `Test on Python 3.11 (ubuntu-latest)`)
3. inspect its step array for:
   - whether a step was reached
   - the step order
   - the step conclusion
4. use job-specific logs only when step-level detail is needed

## 4. Execution pattern to keep

When a CI fix changes behavior but may not trigger automatically:
1. land the minimal fix commit
2. verify whether `push.paths` would have triggered the workflow
3. if not, dispatch `workflow_dispatch`
4. use that run as the authoritative verification artifact
5. post the reason for the manual dispatch in the issue so the audit trail is clear

## 5. Closeout wording guidance

If the fix materially improved the workflow but revealed a new narrower blocker:
- say `landed-but-still-blocked`
- state what failure class was removed
- state the newly exposed blocker
- keep the issue open unless the explicit acceptance gate is truly satisfied

Example progression:
- Windows checkout `invalid path` failure removed
- Ubuntu smoke step now reached and passes
- New blocker exposed: Windows smoke step fails because the command is Bash-style under PowerShell

That is real progress, but not closure.
