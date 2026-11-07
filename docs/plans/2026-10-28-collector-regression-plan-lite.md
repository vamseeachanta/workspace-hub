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

Linux validation will require all 77 collector, provenance and shared-helper
consumer cases to pass without skips. Direct file checks will cover Python syntax,
the engineering register, secrets, publication identifiers and Git LFS attributes.
Hosted check failures will be examined against current main before assigning
them to this change. Linux execution will not establish native Windows or macOS
behavior. The Windows failures below will remain active regression tests, with
no skip markers or production collector changes in this pull request.

## Observed platform limits

The review at `17bb80ff` reports that #3821 reproduces on Windows with Git Bash
and Python 3.12. On 7 November 2026, the merge with main `19da5845` failed four
excluded-volatility cases (`checkout_sha`, `headroom`, `context_md_mtime` and
`job_count`) and the stable-capability rewrite case. Their report comparisons
found an additional change in `generated_at`. The targeted rerun at 10:00–10:02
UTC recorded 5 failed and 1 passed; only the `generated_at` volatility case passed.
These observations supersede the earlier claim that #3821 was not reproduced.

The same review records these full readiness-suite results on Windows:

| Tree | Failed | Passed | Skipped | Errors |
| --- | ---: | ---: | ---: | ---: |
| Main `19da5845` | 317 | 531 | 80 | 8 |
| Merge with `17bb80ff` | 130 | 726 | 80 | 8 |

The review attributes 192 formerly failing cases to the shared fixture's
isolation of ambient scheduler, authentication and provider commands. Those
modules now exercise synthetic command outcomes rather than installed services;
explicit fixture stubs retain precedence. This coverage does not establish live
service availability. The counts above are review evidence, not a local rerun.

The 29 October hosted Fast Gate recorded 23 failures. Byte-identical modules on
main do not establish a passing main run, because main did not run that family.
The `batch:broke-tests` label will remain until the maintainers read a fresh Fast
Gate result on current main. No label will be changed by this update.

## Description update

The pull request comment will supply this Plan-lite section for inclusion in the
description while preserving its implementation and measured-results sections.
Updating the description will remain a maintainer action.
