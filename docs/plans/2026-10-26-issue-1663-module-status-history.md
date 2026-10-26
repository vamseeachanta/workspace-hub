# Plan-lite: optional module status history

The change will retain generated status observations for later trend analysis.
It will be limited to the status matrix script and its tests, with this document
recording the acceptance criteria and filesystem constraint.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-26 | Record bounded scope, acceptance checks and publication limits. |

## Bounded change

[`module_status_matrix.py`](../../scripts/analysis/module_status_matrix.py) will
accept an optional `--history-dir`. It will archive the already-generated UTF-8
JSON under a UTC observation name before updating either active report. Without
the option, report behavior and JSON structure will remain unchanged.

## Acceptance checks

The existing tests in
[`test_module_status_matrix.py`](../../tests/analysis/test_module_status_matrix.py)
will check opt-in CLI behavior, preservation across observations, identical reuse,
conflicting reuse, publication failures, partial writes, UTC conversion, UTF-8
bytes and concurrent name reuse. A failed archive operation will leave active
reports and earlier observations unchanged. Identical reuse will leave the
existing archive unchanged; conflicting reuse will fail without replacing it.

[`test_weighted_scoring.py`](../../tests/analysis/test_weighted_scoring.py) will
check that adjacent scoring and trend behavior remains unchanged.

## Filesystem constraint and limits

The history filesystem will need hard-link support within the history directory.
A complete temporary file will be published with a hard link that cannot replace
an existing observation name. This will protect publication from partial writes
and concurrent name reuse. Crash durability and serialization of concurrent
active-report writers will remain outside the change, along with charts, trend
aggregation and decline alert policy.
