# Collector regression coverage

## Plan-lite

The scope will remain test-only regression coverage for collector idempotency,
atomic report publication and shared subprocess isolation. Production collector
code, report schemas and the documented excluded-field contract will remain
unchanged.

Acceptance will require independent byte, inode and modification-time comparisons
for each excluded-field change. A stable core-count change will rewrite the report
with the expected value while preserving every other field. Atomic publication
checks will require readers to observe both complete reports and no partial
report, including when the move utility path contains spaces and a quote. Failed
publication will preserve the previous bytes and metadata and remove temporary
output. Shared command stubs will prevent ambient scheduler, authentication and
provider access while preserving explicit fixture-stub precedence.

Verification will use the configured uv executable and external temporary
directories:

```sh
uv run --no-project --with pytest --with PyYAML python -m pytest tests/readiness/test_collect_equality.py tests/readiness/test_collect_equality_provenance.py tests/readiness/test_collect_equality_ps1_schema.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/../bt-reviewed"
git diff --check
```

The collector, provenance and shared-helper consumer suites will retain all 77
cases without failures or skips. Direct file checks will cover Python syntax,
the engineering register, secrets, publication identifiers and Git LFS attributes.
Hosted check failures will be examined against current main before assigning
them to this change. Native Windows and macOS behavior will remain unverified
by Linux execution.

## Description update

The pull request comment will supply this Plan-lite section for inclusion in the
description while preserving its implementation and measured-results sections.
Updating the description will remain a maintainer action.
