# Windows harness install doctor preparation

The Windows launcher binds the canonical doctor to the scheduled task user's
profile and the selected repository. Skills junctions and uncertain reparse
results require attention. Equivalent runtime links are preserved. Scheduling is
not installed by this change; native Windows execution remains unverified.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add launcher preparation and regression examples before scheduler enrollment. |

## Invocation

From a local Windows checkout, run:

```powershell
powershell -NoProfile -File scripts/windows/harness-install-doctor.ps1
```

`-WorkspaceRoot` and `-GitBashPath` accept explicit existing paths. Defaults use
the script's checkout and known Git for Windows installation locations, following
[`equivalence-sentinel.ps1`](../../scripts/windows/equivalence-sentinel.ps1).
The launcher appends stdout and stderr to a dated
`logs/maintenance/harness-install-doctor-*.log` file and returns the child status.
Missing Git Bash, bootstrap or user profile prevents execution with a nonzero
status. Log creation or append failures also fail the launcher.

The Bash entry point converts `USERPROFILE` with `cygpath`, requires an existing
absolute directory, and sets `HOME` to that directory. It prepends the profile's
`.local/bin` to `PATH`, sets `WORKSPACE_HUB` from its own location, and invokes the
canonical doctor from that checkout. An inherited `HOME`, current directory or
`WORKSPACE_HUB` cannot select another repair target. Environment variables reach
child processes as documented in [PowerShell about_Environment_Variables,
PowerShell 7.5](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables?view=powershell-7.5).

The doctor preserves the current installer policy: existing Claude runtime state
is checked, not migrated; Codex and Hermes links are maintained where their
provider directories already exist. Gemini entry creation remains deferred.
An installer summary with neither created nor unchanged entries remains a failure.

## Worked example

The portable test fixture supplies these inputs without accessing a real profile:

| Input | Fixture value |
| --- | --- |
| Checkout | Temporary directory named `repo with spaces` |
| Converted profile | Temporary directory named `profile with spaces` |
| Inherited profile and repository | Different temporary directories |
| Child result | Explicit fixture exit status `7` |

Method: resolve the converted profile, derive the checkout from the launcher,
prepend the profile tools directory, and replace the Bash entry process with the
doctor. The expected output is the converted profile, the checkout twice
(`PWD` and `WORKSPACE_HUB`), and the profile's tool path. The expected result is
`7`: the fixture explicitly exits with that value and no status transformation is
specified. A companion fixture exits with `0` and expects `0` by the same method.
These are synthetic transport tests, not measured Windows execution.

The skills guard uses the existing
[`is_reparse_point` contract](../../scripts/lib/reparse_guard.sh):

| Probe result | Meaning | Expected doctor result with otherwise healthy inputs |
| --- | --- | --- |
| `0` | Reparse point | `NEEDS-ATTENTION`, exit `1`; contents preserved |
| `1` | Ordinary path | `OK`, exit `0` when native skills exist |
| `2` | Probe unavailable or inconclusive | `NEEDS-ATTENTION`, exit `1`; contents preserved |

The expected statuses follow that declared contract and the doctor's documented
exit convention; they are independent of its output parser. A missing guard also
requires attention. Tests preserve a marker under the skills directory to check
that the report does not mutate its contents.

For link identity, let `L` be the installed symlink and `T` the required runtime.
The test uses a relative target for `L` that resolves to `T`. The condition
`L -ef T` is true when their device and inode identities agree, under
[GNU Bash manual, edition 5.3 (2025), Bash Conditional Expressions](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html).
The expected answer is an unchanged link and no backup. A different file with
identical bytes gives a false identity comparison and is retargeted, preserving
the decoy file. Native Windows path-spelling equivalence still needs local testing.

## Verification

```sh
uv run --no-project --with pytest --with pyyaml python -m pytest tests/readiness/test_windows_harness_install_doctor.py tests/enforcement/test_soul_auto_load.py tests/readiness/test_windows_scheduler_single_source.py -q -rA -p no:cacheprovider
bash scripts/maintenance/tests/test_harness_install_doctor.sh
uv run --no-project --with ruff ruff check --no-cache tests/readiness/test_windows_harness_install_doctor.py tests/enforcement/test_soul_auto_load.py
```

Native launcher cases require Windows PowerShell and Git Bash. Portable fixtures
exercise profile validation, wrong inherited context, paths with spaces, status
propagation, reparse outcomes and equivalent-link preservation. Passing portable
fixtures does not establish Windows Task Scheduler enrollment or runtime health.

## Remaining slices

[Issue 3750](https://github.com/vamseeachanta/workspace-hub/issues/3750) remains open.

- Add the separate Windows catalog row and explicitly preload and register it in
  `setup-scheduler-tasks.ps1`. A catalog row alone does not register a task.
  Preserve the physical-local scheduler mutation boundary.
- Update the scheduler mutation registry, regenerate the command identity
  inventory, reaffirm the governed source digest and render the indexed HTML
  audit together. Those artifacts contain identifiers outside this contribution's
  publication boundary, and the indexed workflow requires staging authority.
- On Windows, execute the native tests, inspect the installer's path equivalence,
  register locally, and inspect the task action, trigger and last result. The
  existing doctor cadence is defined by the `harness-install-doctor` row in
  `config/scheduled-tasks/schedule-tasks.yaml`; do not invent another cadence.
- Obtain independent review before merge. No live registration, installed-state
  parity or successful unattended repair is established by this preparation.
