# Solver Campaign Runner

The runner starts only approved, resumable campaign drivers. It does not import,
start, query, or license-check a solver. Python 3.11 or newer is required by the
repository; the runner uses only standard-library features available in Python
3.10 and newer.

## Folder Layout

The campaign root is selected by `--root`, then `SOLVER_CAMPAIGN_ROOT`, then the
default home-relative `solver-campaigns` directory. The root contains:

- `approved/<id>.json`: campaign manifests.
- `approvals.tsv`: read-only approval records, one tab-separated line with id,
  manifest SHA-256 digest, approval reference, and date.
- `state/<id>/`: heartbeat, attempt count, next-try time, runner log, and driver
  logs.
- `done/<id>.result`: first line is `STATE<TAB>UTC<TAB>cases_done<TAB>cases_total`.
- `STOP`: global stop file.
- `state/<id>/STOP`: per-campaign stop file.

## Manifest

Fields:

- `id`: short token matching the file name without `.json`.
- `title`: short campaign title.
- `repo_dir`: absolute checkout path.
- `ref`: full 40-character commit id required at checkout `HEAD`.
- `driver`: argument list for the campaign driver.
- `cwd`: driver working directory.
- `env`: string environment additions. Names containing `TOKEN`, `SECRET`,
  `PASSWORD`, `PASSWD`, `CREDENTIAL`, or `KEY` are refused.
- `expected_hours`: expected duration.
- `max_hours`: maximum duration before the campaign is held.
- `progress`: optional `glob` and `total` for case counting.
- `licence_exit_codes`: driver exit codes that mean the licensed solver was not
  available.
- `retry`: `max_attempts`, `backoff_minutes`, and optional
  `licence_tries_per_day` (default: 3).
- `priority`: lower values run first.
- `after`: campaign ids that must be `DONE` first.

Example:

```json
{
  "id": "example-campaign",
  "title": "Example campaign",
  "repo_dir": "/placeholder/checkout",
  "ref": "0123456789abcdef0123456789abcdef01234567",
  "driver": ["python", "drivers/example_driver.py"],
  "cwd": "/placeholder/checkout",
  "env": {"EXAMPLE_MODE": "resume"},
  "expected_hours": 2,
  "max_hours": 6,
  "progress": {"glob": "/placeholder/cases/*.done", "total": 10},
  "licence_exit_codes": [12],
  "retry": {"max_attempts": 3, "backoff_minutes": 30, "licence_tries_per_day": 3},
  "priority": 10,
  "after": []
}
```

`validate <manifest>` prints all validation errors. On success it prints the id
and SHA-256 digest used by the approval gate. A placeholder example can validate
structurally even when its checkout path is not present; `run-once` records the
missing checkout as a preflight failure.

## Approval

The project manager approves a campaign by adding a line to `approvals.tsv`.
Changing a manifest changes its digest and requires a new approval line. The
runner reads `approvals.tsv` only and never writes it.

## States

- `DONE`: driver exit code was zero and progress was complete, or no progress
  rule was declared.
- `FAILED`: non-licence failures exhausted retry attempts.
- `HELD`: a retry, licence hold, incomplete progress, or max-hours condition
  requires a later deliberate action.
- `STOPPED`: a STOP file ended the campaign.
- `pending`, `running`, `unapproved`, `digest-mismatch`, and `invalid` are
  status-only words.

For `HELD`:

- `licence-unavailable`: wait until `next-try`; if the daily cap is reached, the
  next try is set for the next day.
- `driver-exit-<code>`: inspect the driver logs; the runner retries after the
  back-off until `max_attempts`.
- `progress-incomplete`: inspect outputs and manifest progress rules; edit the
  manifest and approve the new digest if the rule was wrong.
- `max-hours`: remove or archive the result file after an operator decides the
  campaign may continue; the runner does not restart it automatically.

## Stop And Release

Create `STOP` in the root to stop all starts. Create `state/<id>/STOP` to stop
one campaign. The content is ignored. Remove the STOP file to release future
starts. A `STOPPED` result remains terminal until the result is deliberately
removed or replaced by an operator.

## Runner Limits

- K1: the runner imports only standard-library modules and no network modules.
- K2: the runner starts only the manifest `driver`; on Windows the single
  permitted process-tree utility is `taskkill`.
- K3: the runner terminates only its recorded child process tree.
- K4: the runner reads checkout metadata and does not delete or modify repository
  files.
- K5: the runner does not commit, push, publish, or use network modules.
- K6: unapproved or digest-mismatched manifests are never run, and
  `approvals.tsv` is never written.

## Exit Codes

`run-once` exits 0 when nothing is eligible, another runner holds the lock, or
one campaign reaches a recorded state. It exits non-zero only for a runner fault.
`status` exits 0. `validate` exits 0 on success and non-zero when any manifest
error is found.

## Scheduled Task

After merge, the workstation owner runs `register-solver-campaign-task.bat` once
by hand. The merge itself installs nothing. The file registers two interactive
scheduled tasks for the current user: a 10-minute task and a logon task. The
action runs `run-solver-campaigns.bat` through hidden, profile-less PowerShell.
No password is requested or stored. The registered tasks run only while the user
is logged on; after a reboot, work resumes at that user's next logon, not before.
The registration uses no task run-duration limit. If the scheduler still ends a
process externally, the next call treats the lock as stale and resumes the
campaign driver.

`unregister-solver-campaign-task.bat` removes exactly the two task names created
by the register file and does not touch the campaign root.

## Logs

Driver stdout, driver stderr, and runner logs rotate in `state/<id>/`. Each file
is capped at 1 MiB with three retained rotations.

## Test Boundary

The tests use a fake driver and temporary campaign roots. They do not establish
whether the licensed solver can be started from a scheduled task on a given
workstation. The first approved campaign will show it; if the solver cannot
start there, the runner holds the campaign and says why.
