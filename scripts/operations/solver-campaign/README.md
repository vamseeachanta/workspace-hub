# Solver Campaign Runner

The runner starts only approved, resumable campaign drivers. It does not import,
start, query, or license-check a licensed solver. Python 3.11 or newer is
required by the repository; the runner uses only standard-library features
available in Python 3.10 and newer.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-20 | Approval storage, numeric validation and crash retry limits are checked before another driver starts. |

## Folder Layout

The campaign root is selected by `--root`, then `SOLVER_CAMPAIGN_ROOT`, then the
default home-relative `solver-campaigns` directory. The root contains:

- `approved/<id>.json`: campaign manifests.
- `approvals.tsv`: approval records, one tab-separated line with id, manifest
  SHA-256 digest, approval reference, and date. Every campaign needs a line added
  by a person.
- `state/<id>/`: heartbeat, attempt count, next-try time, runner log, and driver
  logs.
- `done/<id>.result`: first line is `STATE<TAB>UTC<TAB>cases_done<TAB>cases_total`.
- `STOP`: global stop file.
- `state/<id>/STOP`: per-campaign stop file.

The folder `requested/` is ignored in this release. A `policy.json` file is not a
source of approval; `run-once` logs `standing approval is not available in this
release` when it is present and then continues with person-approved campaigns.
Standing approval is planned as a separate change.

## Manifest

Fields:

- `id`: short token matching the file name without `.json`.
- `title`: short campaign title.
- `repo_dir`: absolute checkout path.
- `ref`: full 40-character commit id required at checkout `HEAD`.
- `driver`: argument list for the campaign driver. The first item is either an
  absolute program path or a program resolved from `PATH`; relative program paths
  with a directory component are refused by `validate`.
- `driver_file`: optional driver script path relative to `repo_dir`; used only as
  a presence check before start.
- `cwd`: driver working directory.
- `env`: string environment additions. Names containing `TOKEN`, `SECRET`,
  `PASSWORD`, `PASSWD`, `CREDENTIAL`, `KEY`, `PASS`, `PWD`, `AUTH`, or
  `COOKIE` as separated tokens are refused.
- `expected_hours`: expected duration.
- `max_hours`: maximum duration before the campaign is held.
- `workers`: optional declared worker count. The runner records the value in the
  manifest form but does not enforce it or pass it to the driver.
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
  "driver_file": "drivers/example_driver.py",
  "cwd": "/placeholder/checkout",
  "env": {"EXAMPLE_MODE": "resume"},
  "expected_hours": 2,
  "max_hours": 6,
  "workers": 1,
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
missing checkout as a preflight failure. `status` and `validate` are read-only:
they do not scan `requested/`, start git, or append approval records.

## Approval

The campaign root and the resolved `approvals.tsv` target must be outside Git
checkouts. `run-once` refuses repository-owned locations before creating state,
lock files or logs. Both ordinary checkouts and linked worktrees are recognized.
An empty directory named `.git` alone does not establish a checkout. This is a
placement check, not an operating-system access boundary: the root and its
contents must be controlled by the maintainer, without concurrent path changes.

A person approves a campaign by adding a line to `approvals.tsv`. Changing a
manifest changes its digest and requires a new approval line. A line whose
approval reference is `policy` does not approve anything in this release.

Approving a manifest approves that manifest only. The driver inherits the
runner's environment, the registering account's Python user site, and any other
process state available to that account. Approval of a manifest is not approval
of those inherited inputs.

## Limits and worked retry example

The source of these state rules is the
[campaign runner requirement](https://github.com/vamseeachanta/workspace-hub/issues/4066),
under Approval gate, Resilience and Limits of the runner. No physical equations,
standards-derived coefficients or engineering acceptance limits are introduced.
Durations and retry delays must be finite numbers; booleans are refused.
`retry.max_attempts` must be a positive integer. Licence exit codes must be
positive integers because zero denotes driver success.

Inputs for a synthetic example are `retry.max_attempts = 2`, a recorded attempt
count of `2`, no live recorded driver, and an unchanged approved manifest. The
remaining start budget is calculated as the declared maximum minus recorded
starts: `2 - 2 = 0`. The next invocation writes `FAILED` with reason
`attempts-exhausted` and does not start a driver. Completed case files and the
recorded attempt count remain unchanged. This also applies when the last start
ended in a crash before a terminal result was written. Below the maximum, the
existing driver is restarted and remains responsible for skipping completed
cases. A licence-unavailable exit restores the preceding attempt count and uses
the existing next-try delay instead.

The regression test `test_exhausted_crash_attempt_is_not_restarted` supplies
these inputs independently and checks the result and absence of driver output.
The repository-root and approval-symlink tests compare checkout snapshots before
and after refusal. Numeric rejection tests use synthetic invalid inputs; they
are format and state-machine checks, not qualified engineering results.

## States

- `DONE`: driver exit code was zero and progress was complete, or no progress
  rule was declared.
- `FAILED`: non-licence failures exhausted retry attempts.
- `HELD`: a retryable condition is waiting for `next-try`, or an operator-held
  condition requires a later deliberate action.
- `STOPPED`: a STOP file ended the campaign.
- `pending`, `running`, `unapproved`, `digest-mismatch`, and `invalid` are
  status-only words.

For `HELD`:

- `licence-unavailable`: wait until `next-try`; if the daily cap is reached, the
  next try is set for the next day.
- `driver-exit-<code>`: inspect the driver logs; the runner retries after the
  back-off until `max_attempts`.
- `driver-start-failed`: inspect the driver path, account rights, and working
  directory; the failed start counts as an attempt and is retried after the
  back-off until `max_attempts`, then recorded as `FAILED`.
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
- K2: the runner starts only the manifest `driver`.
- K3: the runner terminates only its recorded child process tree.
- K4: the runner reads checkout metadata and does not delete or modify repository
  files.
- K5: the runner does not commit, push, publish, run git, or use network modules.
- K6: unapproved or digest-mismatched manifests are never run, and the runner
  never writes `approvals.tsv`.

## Exit Codes

`run-once` exits 0 when nothing is eligible, another runner holds the lock, or
one campaign reaches a recorded state. It exits non-zero only for a runner fault.
`status` exits 0. `validate` exits 0 on success and non-zero when any manifest
error is found.

## Running without a person at the keyboard

The workstation administrator runs `register-solver-campaign-task.bat` once. With
no mode argument, it uses `batch`. The root argument is required and must be an
existing folder. The argument form is
`register-solver-campaign-task.bat [batch|batch-password|desktop] root [--dry-run]`;
unknown arguments, empty arguments, duplicate modes, extra arguments, and unknown
options are refused. Run the dry run first to print the task definition and
resolved campaign root without registering it. The root may contain spaces, but
must not contain `(`, `)`, `&`, `^`, `%`, or `!`.

The modes are:

- `batch`: runs as the registering account whether or not a desktop session is
  active, without storing a password. This is the default because some
  workstations refuse licensed-solver access from a network logon, and a batch
  logon is not a network logon. `S4U` mode has no stored network credentials, so
  shares and authenticated network resources are unavailable. Batch modes need
  rights to create a boot-trigger task. Whether that requires an elevated prompt
  depends on workstation policy and is not established by these tests. When
  registration is refused, the register script prints `Task registration failed.
  Check rights for the selected mode.` and exits with the task registration
  command's exit code.
- `batch-password`: runs as the registering account with the password prompt
  handled by the task registration command.
- `desktop`: runs only while the registering account is logged on to the desktop
  session. A console window appears on each scheduled start and remains open for
  that runner invocation; closing it ends the runner and the active driver tree.

The first campaign under `batch` is the license-access test. If it is held on a
license error, the administrator registers again as `batch-password`. If that
also fails, the administrator registers again as `desktop`.

Each new campaign is picked up by the next `run-once` call after a manifest is
placed in `approved/` with an approval line. Progress is read from `status`; the
first line is `task-mode <batch|batch-password|desktop|unknown>`. Batch modes
include a startup trigger, so a reboot starts the runner again. Desktop mode does
not run after a reboot until that account logs on. A runner crash ends the driver
tree through the job object; the next call restarts the campaign and counts
another attempt. The scheduled action runs the runner code present in the
checkout at the time the task starts. The form and encoding of the registered
account returned by the task service are confirmed during the first registration
read-back.

Create `STOP` in the root to stop new starts and end the active driver's whole
tree. `unregister-solver-campaign-task.bat` removes the scheduled task and the
task-mode record, and does not touch campaign data. A stopped or held campaign
resumes only after the relevant STOP file or terminal result is deliberately
removed or replaced.

The runner lock is an operating-system lock held on an open file. The JSON in the
lock file is diagnostic only; process id, boot-time, or wall-clock heuristics do
not decide lock ownership.

Use a short campaign root when possible. Long paths can exceed limits in command
processors, wrappers, or tools that the driver starts, even when Python itself
can open the path.

## Logs

Driver stdout, driver stderr, and per-campaign runner logs rotate in
`state/<id>/` between starts. A single run can grow beyond the rotation limit
until the next start rotates it. The wrapper's `state/task-runner.log` is not
rotated by the wrapper.

## Test Boundary

The tests use a fake driver and temporary campaign roots. They do not establish
whether the licensed solver can be started from a scheduled task on a given
workstation. The first approved campaign will show it; if the solver cannot
start there, the runner holds the campaign and says why.
