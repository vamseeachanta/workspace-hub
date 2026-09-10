# OrcaFlex execution discovery evidence — 2026-09-09

Scope: read-only investigation and temporary native smoke; no runtime deployment changes.

## Repository revisions

| Repo | Deployed/local HEAD | Fetched upstream main | Divergence local/upstream |
|---|---|---|---|
| workspace-hub plan base | 717aefca741aba35165f7763292948871ef1b94d | not refreshed for deployment | isolated plan worktree |
| digitalmodel | 87d56cac637f971ca3ed57d8ca98c16a845ff0f7 | 61e0c9c25a033b046cff0ff75e4c7b2be8ed5db2 | 0 / 151 |
| Deckhand | 3de8dbabbf2c8f1644b8d73ee238f291aa8c436e | ea24989c521dcab30ba5428cc5c8f791d273ed36 | 1 / 22 |

Commands: `git fetch origin main --quiet`, `git rev-parse HEAD origin/main`, `git rev-list --left-right --count HEAD...origin/main`. Working checkouts were not switched or reset.

## Native proof and diagnostic reproduction

`uv run --no-sync python -B tests/solvers/orcaflex/run_tests.py --check` on the Windows executor returned API available and licence valid. A temporary in-memory line model using its existing environment returned:

```text
OrcaFlex: 11.6c
Statics: InStaticState ; end-A tension: 40.357544807932
Dynamics: SimulationStopped ; complete: True ; finite samples: 31
Saved simulation reload: PASS; bytes: 72612
PASS; temporary simulation removed; elapsed seconds: 0.66
```

The diagnostic false-zero issue was reproduced at 2026-09-09T17:54Z, without changing source or loading a licence:

```python
import runpy, sys
from unittest.mock import patch
with patch('digitalmodel.solvers.orcaflex.core.model_interface.check_orcaflex_available',
           return_value={'has_module': False, 'has_license': False}):
    sys.argv = ['run_tests.py', '--check']
    try:
        runpy.run_path('tests/solvers/orcaflex/run_tests.py', run_name='__main__')
    except SystemExit as exc:
        print('REPRO missing API/licence exit:', exc.code)
```

Output: API Not Available; License Invalid/Missing; Environment check complete; `REPRO missing API/licence exit: 0`.

Other batch findings are static-code findings, not claims of reproduced native failures. At both inspected revisions, `orcaflex_run_batch.py` logs `summary["failed"]` then returns cfg; the executor calls Model without threadCount; case rendering derives names from stems and relocates variant YAML. Implementation will reproduce each defect in RED tests before editing.

## Upstream reuse verified via git show / ls-tree

- Deckhand upstream runtime contains timeout and process-tree termination; configured solver_root; queue reliability fixes; solver-smoke-test allowlisting. Deployed runtime lacks those later changes. Upstream still accepts unbound `verified:true` and legacy text PASS markers.
- Digitalmodel upstream contains `scripts/solver_smoke_test.py`, `src/digitalmodel/solvers/smoke/probes.py`, `workflow.py`, and `run_contract.py`. The smoke runs real statics/dynamics and reloads data, but does not explicitly reject nonfinite results or reload the saved simulation. Existing batch and old check script are unchanged upstream.
- The prototype outside the repos is untracked and uses a different lock path and locking primitive from Deckhand. Its dispatcher uses a shared current-run pointer. This is a contention risk by source inspection; no concurrent live jobs were launched to demonstrate it.

## Live operational observations

- Windows sshd: Running. DeckhandLicensedRunAgent: Running, Password logon. OrcaFlexDigitalmodelRun: Ready, Interactive logon.
- Local queue executor heartbeat: last_poll_at 2026-09-09T17:49:38Z, polls 19261. Fresh heartbeat proves polling only, not end-to-end solver readiness.
- Primary Linux producer: SSH authenticated, hostname returned and uv resolved in a noninteractive session. This proves reachability, not remote OrcaFlex submission. Three expected repo checkouts were observed there.
- Local first-level checkout set includes workspace-hub, digitalmodel, Deckhand, private scope/queue/results checkouts, and the untracked prototype. No all-machine coverage claim was made.
- Existing digitalmodel residue: seven unit-box benchmark modifications. Workspace-hub main already has memory/state/session-report changes. Deckhand working tree is clean but carries a local-only commit. These were preserved.
- The documented coordination claim script is absent in this checkout. Existing worktrees/processes were enumerated; planning uses a dedicated branch/worktree and two read-only inventory agents. No implementation unit was claimed or started.

## Issues checked live

`gh issue view` / `gh issue list` verified OPEN: [coordination](https://github.com/vamseeachanta/workspace-hub/issues/3831), [production epic](https://github.com/vamseeachanta/deckhand/issues/572), [batch onboarding](https://github.com/vamseeachanta/deckhand/issues/550), [batch runner](https://github.com/vamseeachanta/digitalmodel/issues/1554), [neutral ANSYS scope](https://github.com/vamseeachanta/deckhand/issues/543), [dispatch surface](https://github.com/vamseeachanta/deckhand/issues/582). CLOSED: [native smoke implementation](https://github.com/vamseeachanta/digitalmodel/issues/1943), [smoke allowlisting](https://github.com/vamseeachanta/deckhand/issues/588). Issue labels alone do not establish deployed capability.

## Documents and search coverage

Consulted: workspace-hub issue-plan template/planning skill; pre-completion cleanup skill; parallel-first standard; prior OrcaFlex dispatch handoff dated 2026-07-26; Deckhand licensed-run operations/onboarding docs; prototype README and host configuration (private details omitted); digitalmodel workflow registry and batch tests.

Drive search command: `scripts/data/drive-index-search/search.py 'OrcaFlex remote execution' --json --caller plan-resource-intel --limit 3 --timeout-per-index 1`. No matches; five indexes unreachable, one catalog accessible. This is incomplete coverage, not proof that no relevant drive files exist. The search wrote its standard ignored metrics entry.

No new engineering calculations or standards-derived constants were proposed; standards citation sidecars are not applicable. No external notifications or production runs were sent. The local native test's files were removed by TemporaryDirectory cleanup.

## First repair: engine batch acceptance

Post-merge acceptance: the user explicitly authorized merging PR 2081. GitHub reports MERGED at 2026-09-10T02:07:36Z, commit `80da6e09b649707ef7bdb09c9d112f1650bf3d6a`. The isolated worktree was detached at that exact revision; source and contract tests match reviewed `ce372809`. Revalidation passed 54 tests with one skip. A fresh native 11.6c engine run completed statics/dynamics and saved-simulation reload with four finite tension samples, PASS and exit zero. [Sanitized merged proof](2026-09-09-orcaflex-merged-proof.json) records timestamps and hashes. Production tasks, environments and queues were not changed. Earlier observations below remain historical evidence.

Under the user's instruction to continue the proposed sequence, the isolated digitalmodel branch `bugfix/orcaflex-batch-reliability` repairs the packaged base config, native scalar rendering and central failure verdict for [1564](https://github.com/vamseeachanta/digitalmodel/issues/1564) and [2051](https://github.com/vamseeachanta/digitalmodel/issues/2051).

At 2026-09-10T00:18:49Z (9 September local time), the real engine CLI on the patched source ran one exported generic line through statics and dynamics on DLL 11.6c. It saved and reloaded a simulation, reached SimulationStopped and returned four finite effective-tension samples. Summary: completed=1, failed=0, mock=false; central verdict PASS; CLI exit 0. The batch used one process, with the executor's default internal solver thread count. The proposed one-thread resource guard is not yet enforced.

An earlier run during this repair failed at dynamics because a blank RestartStateRecordingTest became literal `~`. That run correctly returned exit 1 and preserved diagnostics. New RED-first regressions and a SafeLoader subclass now preserve blank text separately from explicit numeric-default tokens. The final focused test command passed 54 tests with one skip; additional converter coverage passed 20 tests with two skips.

Detailed sanitized hashes, exact bounded input and limitations are in digitalmodel's `docs/reports/orcaflex-batch-reliability.html` and `orcaflex-batch-native-proof.json` on the repair branch. Raw generic proof directories are intentionally retained locally as audit evidence. The existing production environment and tasks remain unchanged. Neither Linux-origin dispatch nor scheduled-task execution has been accepted by this test.

The [operational runbook](../solver/orcaflex-execution-runbook.html) now links the existing owner map, supported command templates, qualification method, recovery boundaries and ordered next work. Root/batch/readiness skills route agents to it. Claude and Codex review this bounded repair independently; review dispositions accompany the implementation rather than changing approval labels.
