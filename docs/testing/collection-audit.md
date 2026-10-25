# Detecting files hidden from pytest collection

The collection audit compares an independent filesystem inventory with actual
pytest collection. It reports hidden files and fails a successful pytest command
when collection coverage is incomplete. This is shared tooling for issue #3790;
it does not establish that the affected repositories have been triaged.

## Revision history

| Revision | Date | What changed and why |
|---|---|---|
| Initial | 2026-10-22 | Added an independent inventory and observed collection guard to expose invisible test files. |

## Method and evidence

The filename universe is the union of `test_*.py`, `*_test.py`, and pytest's
configured `python_files` patterns. The first conventions are specified in
[the issue plan, OQ1](../plans/2026-08-03-issue-3790-hidden-test-files.md).
The inventory traverses the on-disk tree below pytest's `rootdir` independently
of `testpaths`, `norecursedirs`, `--ignore`, `--ignore-glob`, `collect_ignore`,
`collect_ignore_glob`, and `pytest_ignore_collect`. Untracked and Git-ignored
candidate files are included. Only directories named `.git` are pruned.
The inventory is taken before collection and reconciled at session finish, after
all collection-finish callbacks and wrapper teardowns have returned. Newly
generated candidates are added without discarding the initial set. When tests
execute, candidates generated during execution are included in that final check.

Let F be candidate files, C files with observed pytest items, and S files with
observed, reasoned module skips. The unresolved set is `U = F - C - S`.
This is set subtraction, derived from the issue plan's R-A invariant; there are
no physical coefficients or empirical acceptance limits. A successful audit
requires U to be empty, completed collection, a nonempty inventory, no collection
errors, and valid reasons on exclusion markers. No numerical tolerance applies.

The plugin observes `pytest_itemcollected`, `pytest_deselected`,
`pytest_collectreport`, and `pytest_collection_finish`, then writes its result
at `pytest_sessionfinish`. These interfaces and configuration semantics are
documented in the [pytest reference](https://docs.pytest.org/en/stable/reference/reference.html#collection-hooks)
and [python_files configuration](https://docs.pytest.org/en/stable/reference/reference.html#confval-python_files),
retrieved on 2026-10-22. This avoids approximating executable conftest hooks by
reading comments or matching their source text.
The synthetic regressions and worked example were exercised with pytest 9.1.1.

## Use

Place environments, generated outputs, and audit reports outside the audited
checkout. Run from the repository root with its normal dependencies available.
`HUB` identifies the checkout containing this tool, `REPO` the audited checkout,
and `AUDIT_REPORT` an output file outside it. The report's parent must exist.

Inventory only, without importing tests or conftests:

```bash
python "$HUB/scripts/testing/collection_audit.py" --inventory "$REPO" > "$AUDIT_REPORT"
```

Every file in this output is `NOT_EVALUATED`: the command establishes names,
not collection, execution, obsolescence, or a justified exclusion. The standalone
command uses both conventional filename patterns; configured extra patterns
are included by the pytest plugin.

For a collection audit, run the repository's normal full collection command with
the plugin enabled. An example invocation is:

```bash
cd "$REPO"
PYTHONPATH="$HUB/scripts/testing${PYTHONPATH:+:$PYTHONPATH}" \
  python -m pytest -p collection_audit --collect-only -q \
  -p no:cacheprovider --audit-test-collection "$AUDIT_REPORT"
```

The plugin has no effect unless `--audit-test-collection` is supplied. It does
not disable repository plugins, override configuration, import additional test
files, or run a second collection. Normal collection can execute import-time code;
an inventory-only run is the appropriate initial step when collection has not
been qualified for the available dependencies or licensed software restrictions.

Each JSON row records a repository-relative path, collection status, observed
item count, deselected count, and exclusion-marker evidence. Module skips also
record the observed reason. Collection failures keep their original nonzero
pytest exit code. A successful pytest exit becomes a failure if the audit fails.
The report's `PASS` describes collection coverage; an execution failure still
fails pytest even when collection coverage passes.

Files skipped through `skip` or `skipif` require a nonempty reason. A custom
condition selected out by `-m` must have a registered marker and an explicit
`reason` on the observed item. For example:

```python
@pytest.mark.conditional(reason="named dependency unavailable")
def test_optional_feature():
    ...
```

Register `conditional` in pytest's `markers` configuration and select it with
the appropriate marker expression. A reasoned marker on a file that remains
hidden by a path filter does not satisfy the audit. A module-level skip is
reported separately and must also have an observed nonempty reason.

## Worked example: a hidden file

Use a disposable example directory containing these inputs:

`pytest.ini`:

```ini
[pytest]
testpaths = tests
```

`tests/test_visible.py`:

```python
def test_visible():
    assert True
```

`tests/test_conditional.py`:

```python
import pytest

@pytest.mark.skipif(True, reason="synthetic unavailable dependency")
def test_conditional():
    assert True
```

`legacy/test_hidden.py`:

```python
def test_hidden():
    assert True
```

Hand calculation: F contains the three named files. C contains the two files
under `tests`; S is empty because `skipif` leaves its item collectable. Therefore
U contains exactly `legacy/test_hidden.py`. The audit exits with failure and
reports that file as `not_collected`. The marker reason is recorded for
`tests/test_conditional.py`.

Change `testpaths = tests` to `testpaths = .` and repeat the command. The three
files now appear in C, U is empty, and collection reports `PASS`. Running the
same command without `--collect-only` executes the example: two tests pass and
one is skipped. Those expected counts are obtained by directly counting the
fixture functions and its explicit true skip condition, independently of the
audit implementation. The regression suite exercises the corresponding set
subtractions and exclusion cases.

## Adoption and remaining triage

The guard covers an inventory, observed reconciliation, and recurrence tests.
It does not attribute a hidden file to one particular filter: several filters
may hide the same file. A successful module collection that produces no items
remains unresolved, so empty or obsolete test-shaped files require inspection.
Only collection-time skips are reported as skipped in a collection-only run;
an observed item is not evidence that its test body passed.

Use a serial, full-root collection command. Partial path selections are compared
against the full inventory and normally fail. Distributed collection is not
supported. A narrowed `rootdir` narrows the evidence scope; callers must use the
repository root. Unreadable directories, directory symlinks, and directory
junctions fail explicitly instead of silently reducing coverage. Candidate file
symlinks also fail.
Configured patterns that hide conventional test files cannot narrow F.

The three target checkouts are unavailable in this worktree. Their exhaustive
inventories, individual reruns, verified dispositions, marker migrations,
collected-count changes, and CI adoption remain **NOT_EVALUATED**. No existing
suppression is broadened or removed by this tooling change. Maintainers must
complete that work before treating issue #3790 as resolved.

Audit reports retain marker and skip reasons verbatim. Review those reports
before publication; do not publish private paths or other restricted evidence.
