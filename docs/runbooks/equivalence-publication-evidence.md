# Equivalence publication evidence

A declared schedule does not establish that a fingerprint reached the shared
state ref. The read-only diagnostic checks a pinned local snapshot, the local
publish receipt, and the equality report together. Its result applies only to
those captured inputs; it does not establish live scheduler installation,
authentication, remote-ref currency, or a deployed matrix page.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Add captured-evidence checks and a worked example to distinguish configured schedules from observed publication. |

## Basis and scope

Issue #3505 requires a published fingerprint and a green matrix publish-health result.
The linked monitoring issue #3502 and publisher repair #3511
explain the distinction between declared schedules, successful publication and
locally recorded health. Scheduler and publisher repairs already exist in the
repository; this diagnostic makes the remaining evidence checks repeatable.

The acceptance basis is the existing
[`publish_health_verdict`](../../scripts/readiness/build-equality-matrix.py):
`PUBLISH_SLOW_S` permits a duration up to 60 seconds, and `PUBLISH_STALE_H`
permits an age up to 26 hours. These are operational policy limits from the
monitoring contract, not engineering constants or licensed-standard values.
The diagnostic imports both limits and the grader directly. The version and
return-code rules come from
[`validate_fingerprint`](../../scripts/monitoring/equivalence_schema.py) and
[`validate_publish_health`](../../scripts/monitoring/equivalence_state.py).

## Collect and check evidence

Run from an authorized, current checkout on the workstation being diagnosed.
First inspect the existing schedule definition and Windows installer:

- `config/scheduled-tasks/schedule-tasks.yaml`, task `equivalence-sentinel`;
- `scripts/windows/setup-scheduler-tasks.ps1`, `-EquivalenceOnly -WhatIf`;
- `scripts/windows/equivalence-sentinel.ps1`, the canonical Bash wrapper.

A preview shows intended registration. Inspect the materialized
`EquivalenceSentinel` task and its execution history separately. If installation
or authentication is missing, the maintainer must resolve it before attempting
publication. Existing installer and publisher operations change shared state;
this diagnostic neither invokes them nor authorizes their execution. Successful
local collection alone does not prove publication.

After an authorized sentinel cycle and equality collection, capture the current
remote state ref using the normal repository fetch procedure. The exact
fingerprint must appear at `<registry-key>.json` in the captured tree. A bare
`ls-remote` result proves that the ref exists, not that it holds the required
fingerprint. Preserve the capture revision and evaluation time with the result.
Local evidence normally resides in:

- `.claude/state/equivalence/local-fingerprint.json`;
- `.claude/state/equivalence/publish-health.json`;
- `.claude/state/equality-<registry-key>.yaml`.

From PowerShell, provide the exact registry key and the captured local ref:

```powershell
$RegistryKey = Read-Host 'Registry key'
$CapturedRef = Read-Host 'Captured local state ref or commit'
uv run --script scripts/monitoring/equivalence_publish_check.py `
  --repo . --machine $RegistryKey --state-ref $CapturedRef
```

Equivalent Bash invocation:

```bash
read -r -p 'Registry key: ' registry_key
read -r -p 'Captured local state ref or commit: ' captured_ref
uv run --script scripts/monitoring/equivalence_publish_check.py \
  --repo . --machine "$registry_key" --state-ref "$captured_ref"
```

Use `--local-fingerprint`, `--health` and `--equality-report` to select saved
captures explicitly, and `--as-of` to fix an RFC3339 evaluation time. Equality
reports may be YAML or JSON. No Git fetch, publish, scheduler mutation or
credential probe occurs. All Git subprocesses ignore inherited repository
bindings, and the state commit is resolved before tree/blob reads. Evidence
payloads, supplied identities, filesystem paths and Git stderr are not printed.

## Interpretation

| Check | Passing evidence | Otherwise |
|---|---|---|
| `published_fingerprint` | Exact regular JSON blob for the supplied registry key, valid schema and current timestamp | Inspected absence fails; an unreadable ref is `NOT_EVALUATED`. |
| `local_publish` | Same validated fingerprint as the published blob, successful publish-phase receipt, current time and acceptable duration | Missing capture is `NOT_EVALUATED`; invalid, failed or inconsistent capture fails. |
| `matrix_publish_health` | Correct report identity, current generation time, `PUBLISH-OK`, and the same receipt timestamp, duration and return code | Missing capture is `NOT_EVALUATED`; wrong identity, stale generation or mismatched receipt fails. |

A fingerprint or receipt must not be from the future. The receipt cannot precede
the fingerprint, and the equality report cannot precede the receipt. Equivalent
timezone offsets compare as instants. All checks must pass for exit status zero;
any other outcome exits nonzero. `FAIL` takes precedence over `NOT_EVALUATED`.
Reports captured across successive sentinel cycles may fail the consistency
checks; capture a coherent cycle rather than weakening the checks.

A passing captured-evidence result is necessary evidence for recovery, not proof
that the Windows task will run unattended. The maintainer must still inspect the
scheduled run and refresh the deployed matrix through the existing approved
publication procedure before closing the operational issue.

## Worked example

Run the supplied synthetic inputs without accessing Git or the network:

```bash
uv run --no-project --with pyyaml python tests/monitoring/equivalence_publish_example.py
```

Inputs: registry key `example`; local and published fingerprints both timestamped
`2026-10-22T11:00:00Z`; a successful publish-phase receipt timestamped
`2026-10-22T11:00:02Z` with duration 2 seconds; an equality report generated at
`2026-10-22T11:01:00Z` carrying that same receipt; evaluation time
`2026-10-22T12:00:00Z`. These are constructed example values.

Method: age equals evaluation time minus evidence time. By hand, fingerprint age
is 1 hour, receipt age is 59 minutes 58 seconds and report age is 59 minutes.
All are nonnegative and below the cited 26-hour matrix limit. The constructed
2-second duration is below the cited 60-second matrix limit. Identity, content,
receipt values and timestamp ordering agree. The expected answer is:

```json
{
  "status": "PASS",
  "checks": {
    "published_fingerprint": {"status": "PASS", "code": "published-fingerprint"},
    "local_publish": {"status": "PASS", "code": "publish-succeeded"},
    "matrix_publish_health": {"status": "PASS", "code": "PUBLISH-OK"}
  }
}
```

The automated test separately derives the exact boundary case: noon today minus
10:00 yesterday equals 26 hours. Equality with the existing age and duration
limits passes; values beyond them fail. No expected value is computed by the
function under test.

## Follow-up

Live Windows scheduler execution, current remote capture and deployed matrix
refresh remain unevaluated by this repository-only change. A second-provider
review is required before merge. No operational recovery is claimed.
