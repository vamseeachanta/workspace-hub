# Advisory hub test families

The inventory, selector and collection report make Python test coverage
inspectable by directory. The advisory workflow runs only selected families
with successful collection evidence and an evaluated test-body policy.
Existing checks and branch protection are unchanged.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| 1 | 2026-10-22 | Add directory inventory, explanations and conservative advisory execution. |

## Inventory and mapping

`scripts/ci/hub_test_inventory.py` enumerates `test_*.py` under `tests/`,
`coordination/tests/` and script areas. This follows `pyproject.toml`'s Python
test naming convention. It includes nested and adjacent script tests, extending
the one-level `scripts/*/tests/` scope to avoid losing nested data tools.
Symlinks and environment/cache directories are excluded. Shell tests, helper
modules, and names outside the Python convention are outside this inventory.

Families are `tests/<first-directory>`, `tests/root`,
`scripts/<area>/tests` and `coordination/tests`. Every file belongs to one family.
The committed generated artifact is `config/ci/hub-test-families.json`.
The initial tree has 763 Python test files in 85 families; the four new harness
files bring the generated inventory to 767. These are direct counts of the tree,
rather than the approximate count in the issue. The largest groups are
`tests/data` (72), `scripts/data/tests` (49), `tests/enforcement` (47),
`tests/skills` (39) and `tests/cron` (32).

Rules and a rationale for each are in `config/ci/hub-test-rules.json`.
The first matching rule wins. Rule targets are intersected with known families;
an empty code match selects the full inventory. Skills select skills contracts;
configuration and workflows select contract families; script areas select both
embedded tests and the corresponding hub family. Unmapped paths select all
families. Documentation selects none, except definitions or fixtures belonging
to a contract/test area. Changing the inventory convention requires reviewing
this rule contract and regenerating the inventory.

For changed paths P, let F(p) be a rule's selected family set. The answer is
S = union of F(p) over P; selected test files are the union of files in S.
The file count is the cardinality of that union. The set operation and
cardinality basis is *Contemporary Mathematics* (2023), section 1.4, cited below;
the directory policy is specified by issue #4228. No empirical coefficient or
engineering limit is used.
Synthetic expected sets and counts are independently written in test docstrings.

```sh
python -I scripts/ci/hub_test_inventory.py
python -I scripts/ci/hub_test_inventory.py --check
python -I scripts/ci/hub_test_select.py explain --base origin/main --head HEAD
python -I scripts/ci/hub_test_select.py json --base origin/main --head HEAD
```

Explanation is read-only and uses the merge-base diff. Uncommitted changes are
not part of `HEAD`. A saved `git diff --name-status -z --find-renames` stream may
be supplied with `--diff-file`. Both sides of a rename/copy are evaluated;
deletions select from the current inventory. No shell executes the displayed
pytest command. The command is an explanation of selection before health/policy
filtering, so it can include tests that the advisory workflow will exclude.

## Worked example

Inputs: a synthetic inventory has `tests/data/test_one.py`,
`scripts/data/tests/test_two.py` and `tests/skills/test_three.py`.
The diff renames `docs/old.md` to `scripts/data/new.py` and deletes
`tests/skills/test_old.py`.

Method: the old documentation path contributes the empty set; the new script
path contributes `{scripts/data/tests, tests/data}`; the deletion contributes
`{tests/skills}`. Their union contains three families and three literal files.
These counts come from the listed inputs, independently of the selector.
The tests additionally check four complete golden explanations, including
rename and deletion cases, and ten hand-calculated path selections.

Answer:

```text
Selected families: scripts/data/tests, tests/data, tests/skills
Test files: 3
Pytest: python -m pytest -q -- scripts/data/tests/test_two.py tests/data/test_one.py tests/skills/test_three.py
```

## Collection and execution budgets

Generate the [collection health table](hub-test-family-health.md) and its
machine-readable companion with an explicit external scratch directory and a
positive per-family timeout:

```sh
python -I scripts/ci/hub_test_health.py generate --scratch "$TMPDIR/collection" --timeout-seconds "$COLLECTION_TIMEOUT_SECONDS"
```

The timeout is a required experimental input, not an inferred engineering
acceptance limit. The report records it. Collection executes
`pytest --collect-only -q`, with the local conftests and cache writes redirected
or disabled. External plugin autoload is disabled for diagnostic reproducibility.
Collection can therefore differ from a fully provisioned development environment.
Missing dependencies and import-time effects are reported, rather than repaired
by installing the complete project environment.

A diagnostic import-time guard rejects external process launches, network
connections, licensed solver imports and writes outside scratch. This is not an
OS sandbox. Test bodies do not run during collection. Raw logs stay in scratch;
public diagnostics contain exception types and missing dependency names only,
so traceback source and environment values cannot enter generated reports.
Each completed family is cached with a digest of local source/configuration,
inventory, policy, timeout and interpreter inputs. An unchanged case is reused.

`NOT_GATING` means collection failed, timed out or found no tests.
`NOT_EVALUATED` means body effects have not been reviewed; this includes network
and scheduler families. The initial body allowlist contains only `tests/ci`,
whose synthetic tests were run directly. Successful collection alone never adds
a family to that allowlist. The report records collection for every family,
including those with unreviewed bodies.

The workflow has a ten-minute setup/aggregate budget and a thirty-minute test
budget, following the existing `baseline-check.yml` budgets. The four-job fan-out
is an operational rollout input from the task's four-worker ceiling, not a test
acceptance limit. Jobs skip drafts; opening a ready PR triggers discovery.
`Hub test aggregate` runs after dependencies finish, rejects failed/cancelled
discovery and required family jobs, and allows a skipped matrix only when the
selection contains no runnable families. Matrix exclusions are reported in the
workflow summary. No new check is configured as required.

## Sources and limits

- Issue #4228 defines inventory, mapping and advisory scope. The issue contains
  no linked issues or comments at inspection time.
- [Contemporary Mathematics, section 1.4: Set Operations with Two Sets](https://openstax.org/books/contemporary-mathematics/pages/1-4-set-operations-with-two-sets),
  published 2023, accessed 2026-10-22, defines union and union cardinality.
  The multi-path union applies this operation repeatedly; disjoint family
  membership makes the inventory count the sum of family sizes.
- `pyproject.toml` defines the local Python test convention; the
  [workflow baseline](hub-test-pr-baseline.md) records current CI commands.
- [pytest usage](https://docs.pytest.org/en/stable/how-to/usage.html), accessed
  2026-10-22, documents collection-only invocation and test path selection.
- [Git diff manual](https://git-scm.com/docs/git-diff), accessed 2026-10-22,
  documents NUL records, name/status output, renames and merge-base comparison.
- [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax),
  accessed 2026-10-22, documents job conditions, concurrency, permissions,
  matrix execution and timeouts. Saved HTTP receipts are retained in scratch.

The health snapshot measures the local minimal environment, not hosted results.
Collection preceded lint cleanup; the full CI family passed again after cleanup.
Inventory drift is checked by the new workflow; health evidence is a dated
snapshot and must be regenerated when onboarding families. The advisory runner
still fails if a previously collectable evaluated family regresses. Additional
family body reviews and making checks required remain maintainer follow-up.
No licensed solver or scheduler is started by these tools.
