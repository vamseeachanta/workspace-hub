# Job-queue cleanup verification

Scope: [PR 4082](https://github.com/vamseeachanta/workspace-hub/pull/4082),
following the [blocking review](https://github.com/vamseeachanta/workspace-hub/pull/4082#issuecomment-6207589533).

The review's option (b) is followed: the 60-minute activity window is retained
and a later pass is added to the integration example. The main revision merged
for the workflow conflict is `85bcb7a410f6cbdcac7e2dcbcda883e1dabc48cf`.
The queue, model-pin and storage test paths are retained in Baseline Testing.

## Method and evidence

Execution is single-lane because the runner, pump, tests and integration contract
are coupled. Plan inspection targeted starvation below the disk floor, repeated
keep records, accidental job starts and loss of cleanup guards. The later pass
is placed before admission, uses a bounded retry batch and calls the existing
guarded cleanup command. No additional removal path is introduced.

Tests were written first. The initial deferred-cleanup suite reported 20 failed,
2 passed and 1 skipped before implementation; failures identified missing retry
markers and the absent pump call. Disposable repositories and aged fixture
entries are used. Fixture child processes clear inherited Git directory bindings.

| Check | Result |
| --- | --- |
| Original queue suite plus initial deferred suite | 74 passed, 10 Windows skips |
| Final deferred suite, including failed-child backoff | 23 passed, 4 Windows skips |
| Exact Baseline Python selection, including both queue files and model-pin tests | 148 passed, 13 Windows skips |
| Retained model-pin and storage suites | 273 passed, 8 PowerShell skips |
| `bash -n` for runner and Bash launcher | Passed |
| ShellCheck for runner and Bash launcher | Passed through an isolated `shellcheck-py` environment |
| `git diff --check` | Passed |
| Advisory model-ID sourcing scan over changed scripts and workflow | No new literals |

Table 1. Local verification against disposable fixtures; skipped cases are not execution proof.

The final deferred suite covers immediate post-result retention, eventual removal,
new file and administrative activity, lock and pending-job retention, changed
files, missing results, failed probes, invalid intervals, dry-run preservation,
deduplicated keep records, the 32-attempt bound and failed-child backoff.

Local artifact inspection targeted removal bypasses, dry-run mutations, lost main
tests, retry starvation and uncaptured child execution. No unresolved defect was
identified in that inspection. The frozen packet's SHA-256 is
`af622420b80a6e3467d42cfc78f2a95e32e55e8d62579fe5a3f850937b779d01`;
the manifest verifier reported all 10 inputs unchanged. This is local inspection,
not independent provider consensus. Additional model calls are prohibited for
this fix-up, so cross-provider review remains outstanding.

## Limits and next checkpoint

Native Windows execution, including the pump's synchronous Bash child, is
NOT_RUN. Windows-only tests identify disk-hold, empty-queue, pause and dry-run
cases for a separately authorized captured Windows check. Storage measurements
and live integration are not established. No live worktree cleanup, queue start,
solver execution or scheduler installation is performed by this verification.

The existing pump invocation cadence is required for later reclamation. Older
keep-log rows have no marker and require guarded manual re-enrollment. A keep
reason other than recent activity removes its retry marker and requires manual
disposition; a failed child instead backs off for another activity interval.

The PR remains draft. Its description will carry the new-head hosted Baseline
Testing result when available. The next maintainer checkpoint is independent
review and native Windows integration evidence before installation or merge.
