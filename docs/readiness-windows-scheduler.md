# Windows scheduler collection

The equality collector measures Windows scheduled tasks through Git Bash. The
query's leading-slash flags require argument-conversion exclusion before the
native executable starts. The exclusion applies to that command only.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add scheduler collection, diagnostics and regression examples to distinguish measurements from unavailable evidence. |

## Inputs and method

`scripts/readiness/collect-equality.sh` invokes:

```bash
MSYS2_ARG_CONV_EXCL='*' schtasks /query /fo csv /nh
```

[MSYS2 Filesystem Paths, Process Arguments](https://www.msys2.org/docs/filesystem-paths/)
defines `*` as excluding every argument from path conversion. The
[Microsoft schtasks query reference](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query)
defines CSV output and the switch that removes headings. Both sources were
retrieved successfully for this change.

After a successful query, the collector removes carriage returns and counts
quoted CSV records. It searches the task-name column, case-insensitively, for
`repository-sync`, `repo-sync`, `equality-report` or `ecosystem-reconcile`, allowing
an underscore, space or no separator in place of each hyphen. A match sets
`has_repo_sync`. `parity-review`, with the same separator rules, sets
`has_parity_review`. The PascalCase task names follow the existing registrations
in `scripts/windows/setup-scheduler-tasks.ps1`; the aliases preserve the behavior
specified by the issue and its predecessor.

Here-strings feed the matching commands so that an early match in a large
listing cannot cause a broken pipe and invalidate the result under `pipefail`.

## Worked example

Synthetic input, following the documented CSV format:

```csv
"\Automation\EqualityReport","N/A","Ready"
"\Automation\SessionCuration","N/A","Ready"
"\Automation\EcosystemReconcile","N/A","Ready"
```

Independent enumeration gives three quoted records. EqualityReport and
EcosystemReconcile match the sync predicate. None matches the parity predicate.
The answer is:

```yaml
scheduler:
  has_repo_sync: true
  has_parity_review: false
  job_count: 3
```

The regression tests also use a task whose status column contains `RepoSync`:
that status must not affect either predicate. A successful empty listing gives
`false`, `false`, and zero. An unavailable executable gives `unknown` in all
three fields. A failed query aborts collection before output or replacement of
an existing report; it emits a diagnostic with the command and exit status,
excluding raw output that could expose private names or paths.

## Native-call audit and limits

The collector's only direct native Windows call with leading-slash option flags
is this scheduler query. The other Windows branch reads environment overrides;
the provider helper is invoked through Python with long options. POSIX path
operands and helper scripts are not Windows option flags. The PowerShell
companion delegates collection to Git Bash; it needs no additional scheduler
implementation.

The tests execute the scheduler section directly with a fake executable that
rejects converted flags or a missing exclusion setting. They cover both
successful and failed queries, the complete emission path, and preservation of
prior evidence on failure without invoking hardware or solver probes.
Native MSYS conversion and the live Windows task inventories still require
validation on Windows. The existing matrix consumes the scheduler booleans;
this change does not alter its grading policy or the evidence schema.
