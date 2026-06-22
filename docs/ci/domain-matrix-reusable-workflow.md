# Domain Matrix — reusable CI workflow

Shared "modular per-domain CI" scaffolding, hosted in `workspace-hub` so
`worldenergydata`, `assetutilities`, `assethold` (and `digitalmodel`) stop
maintaining near-identical copies of the same three jobs.

- Workflow: [`.github/workflows/domain-matrix.yml`](../../.github/workflows/domain-matrix.yml)
- Epic: worldenergydata#526 · P4: worldenergydata#530
- Reference implementation: worldenergydata#531

## What it does

A PR fans out into **one CI job per touched domain** (plus the always-on
cross-cutting core), so a red domain no longer blocks green siblings and they
run in parallel:

```
discover  ->  test-domain (matrix, fail-fast: false)  ->  aggregate
```

- **`discover`** — checks out with `fetch-depth: 0`, diffs the PR base against
  `HEAD`, and runs the caller's selector with `--emit-matrix` to produce
  `matrix=<json>` and `scope=<str>` outputs. Stdlib only — no dependency install,
  so discovery stays fast.
- **`test-domain`** — `fromJSON(matrix)`, `fail-fast: false`, `max-parallel`
  from input. Installs deps, builds `--deselect` args from the quarantine file
  (supporting both `tests/`-prefixed and rootdir-relative node-id forms), runs
  the test-runner on `matrix.targets`, and **treats pytest exit code 5
  ("no tests collected") as a pass**. Uploads a JUnit artifact per shard.
- **`aggregate`** — `needs: [discover, test-domain]`, `if: always()`. Fails iff
  `discover != success` **or** `test-domain != success`. This is the single job
  to wire as the required status check.

## Inputs

| Input | Default | Purpose |
|-------|---------|---------|
| `selector` | `scripts/ci/select_test_targets.py` | Caller's stdlib selector supporting `--emit-matrix --files-from <file>`. |
| `python-version` | `"3.11"` | Python version installed for the domain jobs. |
| `install-cmd` | `uv sync --all-extras` | Dependency install command per domain job. |
| `test-runner` | `uv run --with pytest-xdist pytest` | Command prefix used to run pytest on the shard targets. |
| `max-parallel` | `10` | Bound on the matrix fan-out (core changes can be many domains). |
| `quarantine-file` | `scripts/ci/quarantine.txt` | Known-broken node-ids to `--deselect` (one per line, `#` comments). |

## Minimal caller example

In the calling repo (e.g. `worldenergydata/.github/workflows/ci.yml`):

```yaml
name: CI
on:
  pull_request:
    branches: [main, develop]

jobs:
  ci:
    uses: vamseeachanta/workspace-hub/.github/workflows/domain-matrix.yml@main
    with:
      selector: scripts/ci/select_test_targets.py
      python-version: "3.11"
      install-cmd: uv sync --all-extras
      test-runner: uv run --with pytest-xdist pytest
      max-parallel: 10
      quarantine-file: scripts/ci/quarantine.txt
```

All inputs have sensible defaults, so a repo that follows the conventions can
call it with no `with:` block at all.

## Resulting status-check names — read this before migrating

> **CRITICAL CAVEAT.** A reusable workflow's status-check name is
> **`<caller-job-id> / <reusable-job-name>`** — *not* the reusable job name on
> its own. With the caller job above named `ci`, the checks become:
>
> - `ci / Discover domains`
> - `ci / Domain <name>`
> - `ci / Aggregate domain results`   ← the one to require
>
> Inlining the same jobs in the caller (the pre-migration layout) produces
> bare names like `Aggregate domain results`. **Adopting the reusable workflow
> therefore RENAMES every check.**

### Branch-protection migration

- **Repos WITHOUT branch protection — `assetutilities`, `assethold`** — adopt
  freely. No required checks exist, so the rename is harmless. Just switch the
  `ci.yml` to `uses:` the reusable workflow and delete the inlined jobs.
- **Repos WITH branch protection — `worldenergydata`, `digitalmodel`** — the
  required check (e.g. `Test (PR gate)`) will no longer report under that name
  once jobs move into the reusable workflow. Perform a **one-time required-check
  rename** when migrating:
  1. Open the migration PR (caller switched to `uses:`).
  2. Let it run once so the new check name (`ci / Aggregate domain results`)
     appears in the repo's check history.
  3. In branch-protection settings, add the new name to required checks and
     remove the old one.
  4. Merge.

  Until step 3, a stale required check can block merges (it never reports), so
  coordinate the protection edit with the merge.

## Why the selector stays per-repo

Only the multi-job scaffolding + quarantine/exit-5 mechanics are shared. Each
repo keeps its **own** `scripts/ci/select_test_targets.py` because module
layouts differ (`src/worldenergydata/<m>/` vs `src/assetutilities/...`, distinct
core paths, distinct always-on sets). The selector is the single source of truth
for *that repo's* file -> target mapping; the reusable workflow only needs it to
emit `matrix=<json>` and `scope=<str>` to `$GITHUB_OUTPUT` using the stdlib.
