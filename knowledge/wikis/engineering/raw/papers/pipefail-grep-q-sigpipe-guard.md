# Archived Skill: `pipefail-grep-q-sigpipe-guard`

Original path: `/home/vamsee/.hermes/skills/development/pipefail-grep-q-sigpipe-guard`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/development/pipefail-grep-q-sigpipe-guard`
Consolidation date: 2026-04-29

---

---
name: pipefail-grep-q-sigpipe-guard
description: Diagnose and fix false negatives caused by `grep -q` short-circuiting upstream producers under `set -euo pipefail`.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  tags: [bash, pipefail, grep, sigpipe, hooks, debugging]
---

# Pipefail + `grep -q` SIGPIPE Guard

Use this when a Bash script running under `set -euo pipefail` appears to report “no match” or “no approval” even though manual inspection shows matching files or lines exist.

## Symptom pattern

Common signature:
- script uses `set -euo pipefail`
- check is written like `producer | grep -q pattern`
- producer is something like `find`, `head`, `cat`, `git`, or another long-running command
- the script falsely fails despite real matches
- reproducing the pipeline shows exit code `141`

Example failure:

```bash
find "$repo/.planning/plan-approved" -name '*.md' -newer "$repo/.planning/STATE.md" | grep -q .
```

If `grep -q` finds the first match immediately, it exits 0 and closes the pipe. `find` then receives `SIGPIPE`. Under `pipefail`, the pipeline status can become non-zero, so the script treats a successful match as failure.

## Root cause

`grep -q` is an early-exit consumer.
With `pipefail`, the shell reports failure if any earlier pipeline stage fails, including failure due to `SIGPIPE` from the consumer exiting early.

So the bug is not “grep found nothing”; the bug is “the producer was terminated after grep already succeeded.”

## Safe fixes

### Preferred: stop the producer at the source

```bash
find "$dir" -name '*.md' -newer "$marker" -print -quit | grep -q .
```

This prevents `find` from continuing after the first match.

### Better when practical: avoid the pipeline entirely

```bash
first_match=$(find "$dir" -name '*.md' -newer "$marker" -print -quit)
[[ -n "$first_match" ]]
```

This is easier to reason about in hooks and enforcement scripts.

### Do not assume this is the same as grep exit 1 handling

A separate pipefail pitfall is `grep` returning 1 for “no matches.”
This skill covers the other case: `grep -q` succeeded, but the producer died with `SIGPIPE` and poisoned the pipeline status.

## Debug workflow

1. Re-run the exact pipeline manually.
2. Capture the pipeline exit code.
3. If it is `141`, suspect upstream `SIGPIPE`.
4. Re-run the producer without `grep -q` to confirm matches exist.
5. Patch to `-print -quit` or a non-pipeline existence test.
6. Re-run the hook/script end to end.

## Good target areas

- pre-commit hooks
- plan/review gates
- approval-marker existence checks
- file-discovery guards
- optional-config detection logic
- repo enforcement scripts that scan large approval-marker directories

## Concrete enforcement-hook example

Observed real failure in `scripts/enforcement/require-plan-approval.sh`:

```bash
find "${repo_root}/.planning/plan-approved/" -name "*.md" -newer "${repo_root}/.planning/STATE.md" 2>/dev/null | grep -q .
```

In a repo with thousands of `plan-approved/*.md` markers, this produced a false blocker under `set -euo pipefail`:
- approval markers really existed
- manual `find` showed matches
- direct pipeline reproduction returned `141`
- pre-commit hook wrongly reported `NO APPROVAL`

Safe patch used:

```bash
find "${repo_root}/.planning/plan-approved/" -name "*.md" -newer "${repo_root}/.planning/STATE.md" -print -quit 2>/dev/null | grep -q .
```

This preserves the existing structure while stopping `find` after the first match.

## Regression-test pattern

When fixing this in repo enforcement logic, add a shell regression test that:
1. creates a temp git repo
2. creates `.planning/STATE.md`
3. creates many newer `.planning/plan-approved/*.md` files (thousands, not just one)
4. stages an implementation file so the gate actually runs
5. executes the gate script under `--strict`
6. asserts exit code 0 when approval markers exist

Important: a single marker may not reproduce the SIGPIPE race reliably. Use a large marker set to force the upstream producer to still be running when `grep -q` exits.

## Minimal reusable rule

If a `pipefail` script uses `producer | grep -q ...` for existence checks, prefer:
- `producer_that_can_quit_early | grep -q ...`, or
- direct assignment plus `[[ -n ... ]]`

Especially in enforcement hooks, do not let `grep -q` short-circuiting create false blocker conditions.
