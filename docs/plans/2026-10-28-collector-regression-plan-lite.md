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
uv run --no-project --with pytest --with PyYAML python -m pytest tests/readiness/test_collect_equality.py tests/readiness/test_collect_equality_provenance.py tests/readiness/test_collect_equality_ps1_schema.py -q -rA -p no:cacheprovider --basetemp="${TMPDIR:?}/bt-reviewed"
git diff --check
```

Linux validation will require the original 77 collector, provenance and shared-helper
consumer cases and twelve timestamp-stub cases to pass without skips. Direct file checks will cover Python syntax,
the engineering register, secrets, publication identifiers and Git LFS attributes.
Hosted check failures will be examined against current main before assigning
them to this change. Linux execution will not establish native Windows or macOS
behavior. The regression tests will remain active without skip markers or
production collector changes in this pull request.

## Observations recorded on 7 November 2026

The review at `2c2ff5d2` withdraws the earlier Windows diagnosis. The timestamp
stub recognized only the format without a UTC option or suffix; main changed the
collector to request `date -u +%Y-%m-%dT%H:%M:%SZ`. The unmatched request reached
the real clock, causing candidate comparisons to fail before the second
publication and snapshot check. Those failures do not establish report rewrites
or reproduce #3821.

After merging main `b268de95`, the uncorrected Linux suites recorded 4 failed
and 73 passed. Eight new timestamp-stub cases recorded 7 failed and 1 passed
before the correction. The corrected stub accepts both timestamp formats with
an optional UTC option and rejects unrecognized `+%Y-%m-%dT…` formats. The merged Linux
suites then recorded 89 passed, zero failures and zero skips with `PYTHONUTF8`
unset. Four additional cases cover context timestamps and passthrough arguments; one
failed before preserving the UTC option. The original seven idempotency and stable-change cases reached their
publication and snapshot assertions successfully. The before-fix failure count
is an observation from one run; its value depends on wall-clock timing.

Native Windows and macOS were not run. Windows remote access was reachable, but
approved remote scratch and cache locations were not configured. Post-fix Windows
behavior and reproduction of #3821 therefore remain unestablished.

The review at `17bb80ff` records these full readiness-suite results on Windows:

| Tree | Failed | Passed | Skipped | Errors |
| --- | ---: | ---: | ---: | ---: |
| Main `19da5845` | 317 | 531 | 80 | 8 |
| Merge with `17bb80ff` | 130 | 726 | 80 | 8 |

Table 1. Historical Windows results from the review at `17bb80ff`; these counts
precede the timestamp-stub correction.

The review attributes 192 formerly failing cases to the shared fixture's
isolation of ambient scheduler, authentication and provider commands. Those
modules now exercise synthetic command outcomes rather than installed services;
explicit fixture stubs retain precedence. This coverage does not establish live
service availability. The counts above are review evidence, not a local rerun.

The 29 October hosted Fast Gate recorded 23 failures. Byte-identical modules on
main do not establish a passing main run, because main did not run that family.
The maintainers will determine the disposition of the existing failing status
after reading fresh hosted results. No label will be changed by this update.

## Description update

The description will record the timestamp-stub correction, the merged-tree
results, shared-fixture coverage and the limits of platform evidence.
