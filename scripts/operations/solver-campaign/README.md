# Solver Campaign Runner

The runner starts only approved, resumable campaign drivers. It does not import,
start, query, or license-check a solver. Python 3.11 or newer is required by the
repository; the runner uses only standard-library features available in Python
3.10 and newer.

## Folder Layout

The campaign root is selected by `--root`, then `SOLVER_CAMPAIGN_ROOT`, then the
default home-relative `solver-campaigns` directory. The root contains:

- `approved/<id>.json`: campaign manifests.
- `approvals.tsv`: approval records, one tab-separated line with id, manifest
  SHA-256 digest, approval reference, and date. A person may edit it directly;
  a valid standing policy may append `policy` approvals under the runner lock.
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
- `driver_file`: optional driver script path relative to `repo_dir`; required
  for policy approval and must also appear in `driver`.
- `cwd`: driver working directory.
- `env`: string environment additions. Names containing `TOKEN`, `SECRET`,
  `PASSWORD`, `PASSWD`, `CREDENTIAL`, `KEY`, `PASS`, `PWD`, `AUTH`, or
  `COOKIE` as separated tokens are refused.
- `expected_hours`: expected duration.
- `max_hours`: maximum duration before the campaign is held.
- `workers`: optional whole-number worker count; required for policy approval.
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
they do not evaluate policy, start git, or append approval records.

## Approval

A person approves a campaign by adding a line to `approvals.tsv`. Changing a
manifest changes its digest and requires a new approval line.

An optional `policy.json` file in the campaign root can approve manifests in
`requested/`. The runner never creates, changes, or deletes that policy file. If
the file is absent, requested manifests are not run, no git process is started,
and `approvals.tsv` is not written. If the file is present and valid, the runner
checks the local clone only: the normalized remote address must match the policy
entry after trimming trailing slashes and case-folding; the manifest ref must be
an ancestor of the clone's recorded remote default branch; `driver_file` must be
tracked at the ref; tracked files must match the ref; files marked skip-worktree
or assume-unchanged are refused; untracked loadable files in the driver folder
and working directory are refused for `.py`, `.pyw`, `.pth`, `.bat`, `.cmd`,
`.ps1`, `.exe`, `.dll`, and `.pyd`; and the id, workers, and hours must fit the
limits. The policy may list interpreter executable names or paths in
`interpreters`. A policy-approved manifest must execute either `driver_file`
directly or one listed interpreter followed immediately by `driver_file`, with no
interpreter option before the driver file. `cwd` must be the checkout or a
directory inside it. `env` must be empty unless the policy lists allowed names in
`allowed_env`; names that change program loading (`PYTHON*`, `PATH`, `PATHEXT`,
and `COMSPEC`) are refused even when listed. A passing request appends one
`policy` line to `approvals.tsv` under the runner lock. A changed manifest is a
new request. Before every policy-approved start, including retries, the runner
rechecks the current policy file and the git conditions under the runner lock.

The policy does not contact a remote service. "Merged" means the clone's
remote-tracking reference as it stood at its last update. Review status is not
checked. The policy refuses a `policy.json` symbolic link and refuses a campaign
root inside a git working tree. Git checks run with `core.fsmonitor=false`,
`GIT_CONFIG_NOSYSTEM=1`, and diff checks use `--no-ext-diff --no-textconv`.
Remote URL rewrite rules in local git configuration can still affect what git
reports. The policy does not inspect every untracked file in the checkout; it
checks the driver folder and working directory for the suffixes listed above. The
`workers` limit gates approval but is not passed to the driver. A user who can
change the checkout git data or the campaign root can satisfy the policy
conditions. The policy is a convenience on a solver workstation controlled by the
workstation administrator, not a protection against a user of that workstation.

## States

- `DONE`: driver exit code was zero and progress was complete, or no progress
  rule was declared.
- `FAILED`: non-licence failures exhausted retry attempts.
- `HELD`: a retry, licence hold, incomplete progress, or max-hours condition
  requires a later deliberate action.
- `STOPPED`: a STOP file ended the campaign.
- `pending`, `requested`, `running`, `unapproved`, `digest-mismatch`, and `invalid` are
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
  permitted auxiliary program for policy checks is `git`.
- K3: the runner terminates only its recorded child process tree.
- K4: the runner reads checkout metadata and does not delete or modify repository
  files.
- K5: the runner does not commit, push, publish, or use network modules.
- K6: unapproved or digest-mismatched manifests are never run, and
  `approvals.tsv` is written only by appending a `policy` line when a valid
  policy approves a requested manifest.

## Exit Codes

`run-once` exits 0 when nothing is eligible, another runner holds the lock, or
one campaign reaches a recorded state. It exits non-zero only for a runner fault.
`status` exits 0. `validate` exits 0 on success and non-zero when any manifest
error is found.

## Running without a person at the keyboard

The workstation administrator runs `register-solver-campaign-task.bat` once. With
no argument, it uses `batch`. The argument form is
`register-solver-campaign-task.bat [batch|batch-password|desktop] [root] [--dry-run]`;
unknown or misplaced arguments are refused. The administrator can also run
`write-solver-campaign-policy.bat` once, then edit `policy.json` to list the
permitted repositories and limits.

The modes are:

- `batch`: runs as the registering account whether or not a desktop session is
  active, without storing a password. This is the default because some
  workstations refuse licensed-solver access from a network logon, and a batch
  logon is not a network logon. Batch modes need rights to create a boot-trigger
  task. When registration is refused, the register script prints
  `Task registration failed. Check rights for the selected mode.` and exits with
  the task registration command's exit code.
- `batch-password`: runs as the registering account with the password prompt
  handled by the task registration command. `S4U` mode has no network
  credentials, so shares and authenticated network resources are unavailable.
- `desktop`: runs only while the registering account is logged on to the desktop
  session. A console window appears on each scheduled start and remains open for
  that runner invocation; closing it ends the runner and the active driver tree.

The first campaign under `batch` is the license-access test. If it is held on a
license error, the administrator registers again as `batch-password`. If that
also fails, the administrator registers again as `desktop`.

Each new campaign is picked up by the next `run-once` call after either a
manifest is placed in `approved/` with an approval line, or a manifest is placed
in `requested/` and a valid policy approves it. Progress is read from `status`;
the first line is `task-mode <batch|batch-password|desktop|unknown>`. Batch
modes include a startup trigger, so a reboot starts the runner again. Desktop
mode does not run after a reboot until that account logs on. A runner crash ends
the driver tree through the job object; the next call restarts the campaign and
counts another attempt. The scheduled action runs the runner code present in the
checkout at the time the task starts.

Create `STOP` in the root to stop new starts and end the active driver's whole
tree. `unregister-solver-campaign-task.bat` removes the scheduled task and the
task-mode record, and does not touch campaign data. A stopped or held campaign
resumes only after the relevant STOP file or terminal result is deliberately
removed or replaced.

The runner lock is an operating-system lock held on an open file. The JSON in the
lock file is diagnostic only; process id, boot-time, or wall-clock heuristics do
not decide lock ownership.

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
