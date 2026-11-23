# Archived Skill: `large-lint-gate-restoration-wave`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/large-lint-gate-restoration-wave`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/large-lint-gate-restoration-wave`
Consolidation date: 2026-04-29

---

---
name: large-lint-gate-restoration-wave
description: Restore a red repository Lint job when flake8 debt is large and mixed, by inventorying outliers, splitting issue ownership, using local direct-venv iteration, inspecting broad auto-format diffs, and closing only after exact local and GitHub Actions Lint proof.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
license: MIT
tags: [ci, lint, flake8, github-actions, dirty-tree, worldenergydata, closeout]
---

# Large Lint Gate Restoration Wave

Use this when a repo's CI Lint job is red from broad legacy flake8/formatting debt, especially when one pathological outlier hides the true remaining backlog and the user expects plan-approved, issue-tracked execution.

## Trigger

- A GitHub issue or umbrella plan asks to restore a Lint job to green.
- The lint inventory has hundreds/thousands of findings across many files.
- One file or module dominates the findings.
- The root/workspace checkout may be dirty, so blind staging is unsafe.
- Final acceptance is the Lint job, not necessarily full CI green.

## Workflow

1. Confirm governance and scope
- Verify the umbrella issue is `status:plan-approved` or otherwise approved for execution.
- Identify child issues for:
  - pathological outlier remediation,
  - safe-rule cleanup outside the outlier,
  - final Lint proof.
- Do not close the umbrella until all children are closed and the pushed main Lint job is green.
- Keep non-lint CI failures explicitly out-of-scope unless the approved plan says otherwise.

2. Build a durable lint inventory first
- Run the exact CI-equivalent lint command and save output to `/tmp`:
  ```bash
  uv run flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv > /tmp/lint-current.txt 2>&1
  ```
- Parse total findings, unique files, dominant files, and code counts.
- Commit a durable report under `docs/ci/` if the inventory is part of the acceptance contract.
- Add or update a provenance test for that report when required by the plan.

3. Normalize the outlier separately
- Fix the dominant pathological file in its own commit/issue.
- Do not satisfy the issue by weakening, excluding, or quarantining the lint gate unless the approved plan explicitly allows that.
- Run targeted tests that exercise behavior around the outlier.
- Commit and push the outlier remediation before broad cleanup.

4. Iterate broad cleanup locally using direct venv commands
- `uv run` can spend minutes compiling bytecode or time out when chained with tests. Prefer direct venv commands for iteration:
  ```bash
  ./.venv/bin/python -m ruff check src --select F401,E402,F541 --fix
  ./.venv/bin/python -m black src tests
  ./.venv/bin/python -m isort src tests
  ./.venv/bin/python -m flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv
  ```
- If line-length and pycodestyle debt remains, use autopep8 cautiously:
  ```bash
  uvx autopep8 --in-place --recursive --max-line-length 100 --select E501 --aggressive --aggressive src
  ./.venv/bin/python -m black src
  ./.venv/bin/python -m isort src
  ```
- Expect automated tools to add `# noqa` for unbreakable long literals/import compatibility and to convert bare `except:` to `except Exception:`. These are acceptable only after diff inspection and final lint proof.

5. Inspect broad dirty tree before committing
- Never `git add .` from a dirty workspace root.
- In the target repo, inspect:
  ```bash
  git status --short --branch
  git diff --name-only | wc -l
  git diff --stat | tail -20
  git diff --numstat | awk '{add+=$1; del+=$2} END {print "additions="add, "deletions="del}'
  git diff --check
  ```
- Verify the outlier file is not accidentally included in the broad cleanup if it had its own issue/commit:
  ```bash
  git diff --name-only | grep -q 'path/to/outlier.py' && echo outlier_dirty=yes || echo outlier_dirty=no
  ```
- Sample representative diffs from high-risk modules and tests before staging.
- Stage only intended directories, e.g. `git add src tests`, from inside the target repo.

6. Final local proof before push
- Run exact acceptance command with `uv run` even if direct venv was used for iteration:
  ```bash
  uv run flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv
  ```
- Also run formatting/import checks:
  ```bash
  ./.venv/bin/python -m black --check src/ tests/
  ./.venv/bin/python -m isort --check-only src/ tests/
  ```
- Record stdout and exits. Clean `uv run flake8` may still print only a bytecode compilation line; treat exit 0 plus no findings as proof.

7. Commit, push, and verify GitHub Actions job-level status
- Commit the broad cleanup with an issue-scoped message:
  ```bash
  git commit -m "style(#ISSUE): clear flake8 safe-rule backlog"
  git push origin main
  ```
- Check the pushed run and inspect jobs, not just the run conclusion:
  ```bash
  gh run list --repo OWNER/REPO --branch main --limit 10 --json databaseId,workflowName,displayTitle,headSha,status,conclusion,createdAt,url
  gh run view RUN_ID --repo OWNER/REPO --json jobs,conclusion,status,url --jq '.url, (.jobs[] | [.name,.status,.conclusion,.databaseId] | @tsv)'
  ```
- If CI run conclusion is failure due non-lint test jobs but the `Lint` job is success, record that caveat explicitly and close only lint-scope issues.

8. GitHub closeout
- Use body files for multiline comments to avoid shell quoting problems.
- For each child issue, include:
  - commit SHA,
  - exact validation commands,
  - local proof snippets,
  - GitHub Actions Lint URL/job status if applicable,
  - explicit caveat for out-of-scope non-lint failures.
- Close child issues first, then umbrella.

## Pitfalls

- Do not weaken lint config or add new exclusions to make the gate green unless the plan explicitly permits it.
- Do not chain `uv run flake8` and long pytest commands in one foreground command if the environment has a 600s timeout; flake8 may finish but pytest can cause the wrapper to time out and obscure evidence.
- Do not rely on overall CI run conclusion when the acceptance criterion is a single job; inspect the `Lint` job status directly.
- Do not close the umbrella issue before the pushed main Lint job is verified green.
- Keep workspace-hub/root dirty-tree safety separate from nested repo commits; never bulk-stage unrelated root artifacts.

## Evidence pattern

A strong closeout comment says:

```text
Pushed main: <sha> <commit message>
Local proof:
- exact uv flake8 command -> exit 0; no findings
- black --check -> exit 0
- isort --check-only -> exit 0
GitHub Actions:
- <run URL>
- Lint job: success
Caveat: non-lint jobs <status> are outside this issue's approved lint-restoration scope.
```
