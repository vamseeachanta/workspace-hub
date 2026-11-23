# Domain Matrix — reusable CI workflow

Shared "modular per-domain CI" scaffolding, hosted in `workspace-hub` so
`worldenergydata`, `assetutilities`, `assethold` (and `digitalmodel`) stop
maintaining near-identical copies of the same three jobs.

## Revision history

| Revision | Date | Change and reason |
|----------|------|-------------------|
| Initial contract tests | 2026-10-22 | Extract decisions, specify selector outputs and add advisory validation to protect callers. |

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
  so discovery stays fast. On non-PR events (`push` / `workflow_dispatch`) the PR
  base SHA is empty, so it falls back to a usable base — see
  [Non-PR events](#non-pr-events-push--workflow_dispatch).
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
| `python-setup` | `"uv"` | How to provision the interpreter in the domain jobs. See [Choosing `python-setup`](#choosing-python-setup). |
| `install-cmd` | `uv sync --all-extras` | Dependency install command per domain job. |
| `test-runner` | `uv run --with pytest-xdist pytest` | Command prefix used to run pytest on the shard targets. |
| `max-parallel` | `10` | Bound on the matrix fan-out (core changes can be many domains). |
| `enforce-contract` | `false` | Report selector and empty-matrix advisories; set to `true` to enforce after review. |
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

## Choosing `python-setup`

The domain jobs need a Python interpreter before `install-cmd` runs. How that
interpreter is provisioned matters because some install commands require the
interpreter to be the **system** python on `PATH`:

| `python-setup` | What runs | Interpreter location | Use when |
|----------------|-----------|----------------------|----------|
| `"uv"` *(default)* | `uv python install <version>` | uv-MANAGED — **not** on `PATH` as the system python | `install-cmd` is `uv sync …` / `uv run …` (the venv-based path; `worldenergydata`, `assetutilities`, `digitalmodel`). |
| `"setup-python"` | `actions/setup-python@v5` (the `uv python install` step is **skipped**) | ON `PATH` as the system python | `install-cmd` is `uv pip install --system …` or any command that installs into the system interpreter (e.g. `assethold`). |

`"uv"` is the original, unchanged behavior — existing callers are completely
unaffected (a caller passing nothing, or `python-setup: uv`, runs exactly the
same two steps as before).

### Why `setup-python` is needed for `uv pip install --system`

`uv python install` installs a **uv-managed** interpreter that is *not* exposed
as the system `python` on `PATH`. `uv pip install --system` targets whatever
interpreter is on `PATH` as the system python — with only a uv-managed
interpreter present, it falls through to the runner's Debian `/usr` python, which
is PEP-668 **externally-managed** and refuses the install. `actions/setup-python`
puts a real interpreter on `PATH` as the system python, so `--system` installs
land there. Repos on the `uv pip install --system` path (e.g. `assethold`)
therefore pass `python-setup: setup-python`:

```yaml
jobs:
  ci:
    uses: vamseeachanta/workspace-hub/.github/workflows/domain-matrix.yml@main
    with:
      python-setup: setup-python
      install-cmd: uv pip install --system -e ".[test]"
```

Implementation: the two provisioning steps are guarded by step-level `if:`
conditions keyed on `inputs.python-setup` (`== 'uv'` vs `== 'setup-python'`), so
exactly one runs. The `discover` job is unaffected — it runs the stdlib selector
with the runner's system `python3` and needs no interpreter setup.

## Non-PR events (push / workflow_dispatch)

The `discover` job diffs the changed files to build the matrix. On
`pull_request` (the primary, required path) it diffs the PR base SHA against
`HEAD` — **unchanged**. On `push` / `workflow_dispatch` the PR base SHA is empty,
which would otherwise yield an empty/spurious matrix, so `discover` falls back in
order:

1. **`pull_request`** — diff `github.event.pull_request.base.sha`...`HEAD`
   (byte-for-byte the original behavior).
2. **`push`** — if the base SHA is empty, diff the push event's `before` SHA
   (`github.event.before`)...`HEAD`, provided it is a real, reachable commit
   (not the all-zeros "new branch" sentinel).
3. **`HEAD~1`** — if `before` is unusable, diff `HEAD~1`...`HEAD`.
4. **Full fan-out** — if no usable base commit exists (orphan / first commit),
   feed the selector a synthetic **core** path (`pyproject.toml`). Every repo's
   selector classifies a core path as `scope=full`, so this fans out the whole
   tree — the safe, fail-open default. (The selectors have no `--all` flag; the
   synthetic-core-path trick is the portable way to force a full run.)

The PR path is untouched; the fallback logic only executes when the PR base SHA
is empty.

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

## Tested aggregate decision

The stdlib helper [domain_matrix_aggregate.py](../../scripts/ci/domain_matrix_aggregate.py)
returns a status and message. Its strict decision is:

`pass = (discover == success) AND (test-domain == success) AND (matrix-size > 0)`.

This is a direct conjunction of the original workflow's job-result checks and
the nonempty-matrix requirement in issue #4227 (2026). There are no empirical
coefficients or engineering acceptance limits. Exit statuses retain the original
workflow convention: `0` for pass, `1` for failure.

For a positive matrix size, the independent hand-written truth table is:

| discover \ test-domain | success | failure | cancelled | skipped |
|------------------------|---------|---------|-----------|---------|
| success | pass | fail | fail | fail |
| failure | fail | fail | fail | fail |
| cancelled | fail | fail | fail | fail |
| skipped | fail | fail | fail | fail |

The same table applies separately to scopes `full`, `modules`, `skip`, and the
empty scope. Scope is diagnostic; `skip` does not waive either job-result check.
A matrix size of zero fails every strict case. An absent count becomes zero;
a negative count also fails. Non-integer CLI input is rejected.

The reusable workflow defaults to **advisory mode** (`enforce-contract: false`):
selector violations and empty matrices produce warnings, while the aggregate
retains its original job-result gate. Set `enforce-contract: true` only after the
maintainer checks both callers. An invalid matrix can still fail GitHub's own
matrix expansion, as before; advisory validation does not override GitHub.

## Selector output contract

The caller's selector writes single-line outputs:

```text
matrix={"include":[{"name":"core","targets":"tests/core","mode":"seq"}]}
scope=modules
```

[validate_selector_output.py](../../scripts/ci/validate_selector_output.py) checks:

- Exactly one `matrix` and one `scope` output; unrelated output keys are ignored.
- Strict JSON: no duplicate object keys or non-finite numbers.
- A matrix object with a nonempty `include` list of objects. Additional matrix
  axes must be nonempty lists; `exclude`, when present, is a list of objects.
- Each include entry has a unique nonempty `name`, containing only ASCII letters,
  digits, `_`, `.` and `-`. This explicit allowlist protects check names.
- Each entry has a nonempty string `targets` and `mode` equal to `xdist` or `seq`.
- `scope` is exactly `full`, `modules` or `skip`.

These are the local contract requirements of issue #4227. Callers should emit
include-only shard matrices; the diagnostic `matrix-size` is the number of
validated include entries, not a Cartesian-product job count. The workflow
continues to read `matrix.name`, `matrix.targets`, and `matrix.mode`.
An invalid contract records `matrix-size=0`, with no untrusted payload in the
validation annotation. Multiline output syntax is outside this line-based contract.

## Worked example: inputs, method and answer

Inputs are the selector output above, discovery `success`, and test-domain
`success`. The validator counts the single include object by hand: matrix size
is `1`. The aggregate evaluates `true AND true AND (1 > 0)`, so the answer is
status `0` and `All domains green`. Scope `modules` supplies context only.

Run the helpers against an output file containing those literal inputs:

```bash
python3 scripts/ci/validate_selector_output.py selector-output.txt
python3 scripts/ci/domain_matrix_aggregate.py success success modules 1
```

Changing the include list to `[]` fails validation. With size `0`, strict
aggregation returns status `1`; advisory aggregation warns and retains the
original success result if both jobs succeeded. These expected answers are
independent Boolean calculations, not values copied from the implementation.

## Quarantine compatibility

[quarantine_args.py](../../scripts/ci/quarantine_args.py) preserves line order,
comments, blank lines, trailing whitespace, quote handling and both node-id
prefix forms. A missing file emits no arguments. Each selected node-id emits
its original form and its alternate `tests/`-prefixed or root-relative form.
As in the original Bash `while read` loop, an unterminated final line is ignored.
NUL-delimited output preserves argument boundaries when loaded into the Bash
array. Tests compare fixture output with the original loop executed locally;
that comparison reports a clear skip if Bash is unavailable.

## Workflow delivery and rollback

The workflow executes in the caller's checkout, where these helpers do not
exist. Their text is embedded into each relevant run step, then written under
`RUNNER_TEMP` at runtime. This makes the helper revision identical to the reusable
workflow revision without fetching a moving branch.

The [GitHub Contexts reference](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
(accessed 2026-10-22) does not document `github.job_workflow_sha`; therefore this
implementation uses the specified embedding fallback. The reference documents
`job.workflow_sha` separately; no undocumented context is assumed.

After changing a helper, regenerate and check the embedded text:

```bash
python3 scripts/ci/embed_domain_matrix.py
python3 scripts/ci/embed_domain_matrix.py --check
```

Static tests parse the YAML and compare embedded source bytes independently of
the generator. Offline shell tests run the embedded steps inside synthetic
caller trees without a tools checkout. Job ids, job names, `if: always()`, and
both aggregate dependencies remain unchanged.

Rollback requires reverting only `.github/workflows/domain-matrix.yml` to its
previous revision. The helpers and tests can remain because the previous
workflow does not invoke them. No caller edit or check-name migration is needed.

Before enabling enforcement, the two callers pinned at `@main` must check:

- Representative selectors for full, module and skip selections satisfy the
  contract, including unique safe names and a nonempty include list.
- Required check names still end with `Aggregate domain results`, and failed,
  cancelled or skipped domain jobs fail the aggregate.
- Quarantined node-ids match both rootdir forms; pytest's no-tests exit continues
  to pass for a shard.
- Advisory output shows the expected include count and no contract warnings
  for representative valid selections.
