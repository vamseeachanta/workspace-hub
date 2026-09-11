# Copy-paste continuation prompt: OrcaFlex model qualification

Continue the existing OrcaFlex qualification work across the repository ecosystem. Qualify the single-line mooring-buoy case first; installation representatives will follow under their own readiness and approval gates. Preserve the distinction between portable source code, native execution readiness, reference equivalence and engineering qualification.

## Bootstrap and authorization

1. Read the destination workspace's applicable `AGENTS.md`, `config/agents/codex/MEMORY.runtime.md`, planning skill and pre-completion cleanup skill. Follow local instructions for the active provider. Check parallel sessions and worktrees before writes; use isolated worktrees and serialize commits.
2. The user authorized merging the current work. This authorizes completing the remaining reviewed merges after their required checks; it **does not authorize a new native attempt**, queue submission, task cutover, credential change or another job. Verify current issue/PR state rather than assuming the snapshot below remains current.
3. Discover actual checkout roots and existing interpreters on this machine. Inspect repository status, branches and worktrees, preserve dirty files, and fetch remote refs without resetting or pulling over active work. Create an isolated clean worktree at the verified integrated revision for further work. Do not synchronize or install environments blindly; first inspect the existing environment and its source bindings.

Run inspection and remote-ref refresh commands from the relevant discovered checkout:

```text
git status --short
git worktree list
git fetch origin
git rev-parse origin/main
gh pr view 2091 --repo vamseeachanta/digitalmodel --json state,mergeCommit,url
gh pr view 2100 --repo vamseeachanta/digitalmodel --json state,mergeCommit,baseRefName,mergeStateStatus,statusCheckRollup,url
gh pr view 3832 --repo vamseeachanta/workspace-hub --json state,mergeCommit,mergeStateStatus,statusCheckRollup,url
```

Do not infer that a checkout already exists at a remembered absolute path. Do not infer that this machine can access artifacts left on the previous Windows workstation.

## Integration snapshot — refresh before acting

| Change | Recorded state |
|---|---|
| [digitalmodel PR 2091](https://github.com/vamseeachanta/digitalmodel/pull/2091), validator repair | MERGED at `14abde3fd96dffc79d802e0329fc9bc090cd270c` |
| [digitalmodel PR 2100](https://github.com/vamseeachanta/digitalmodel/pull/2100), bounded mooring qualification | Integration target: main. Reviewed source `833f8526`; main integration head `8b60410908d758612bfa9571f25c605caa28f340`. Resolve live merge state and merge SHA using the commands above before proceeding. |
| [workspace-hub PR 3832](https://github.com/vamseeachanta/workspace-hub/pull/3832), strategy/reports/handoff | This handover is included in this PR. Resolve its final merge SHA and verify main ancestry at destination bootstrap. |

If already merged, verify the actual merged revision and avoid duplicate changes. If still open, finish the authorized integration only when all required checks and reviews permit it; preserve failed-check evidence and repair within the approved scope. Do not equate a green local suite with hosted CI completion.

## Read the durable record

In workspace-hub, read:

- `docs/reports/orcaflex-pipeline-worklog.html` and `docs/reports/orcaflex-work-log.md`.
- `docs/reports/2026-09-11-orcaflex-family-qualification.html`.
- `docs/reports/2026-09-10-orcaflex-cutover-readiness.html` and `docs/solver/orcaflex-execution-runbook.html`.
- `docs/reports/2026-09-11-orcaflex-local-example-inventory.json` and the Linux inventory beside it.

In digitalmodel at the integrated mooring revision, read:

- `docs/reports/orcaflex-mooring-2093.html`, `.md`, `-native.json` and `-corpus.json`.
- `docs/reports/orcaflex-mooring-2093-reference-differences.json`: all 56 difference paths and value hashes; the original model data remains available through the source library and retained private bundle.
- `docs/benchmarks/mooring_buoy/qualification.yml`, `scripts/prepare_mooring_qualification.py`, and the model-mode arguments in `docs/plans/evidence/issue-2082-native.ps1`.
- Existing model probe, result and manifest modules under `src/digitalmodel/solvers/smoke/` and their fake-API/Windows ownership tests.

Issue ownership:

- [digitalmodel 2093](https://github.com/vamseeachanta/digitalmodel/issues/2093): first mooring qualification.
- [digitalmodel 716](https://github.com/vamseeachanta/digitalmodel/issues/716): corrected offline validator.
- [digitalmodel 2092](https://github.com/vamseeachanta/digitalmodel/issues/2092): existing hash-seed-dependent YAML ordering.
- [workspace-hub 3831](https://github.com/vamseeachanta/workspace-hub/issues/3831): execution ecosystem.
- [Deckhand 591](https://github.com/vamseeachanta/deckhand/issues/591): safe cleanup/quarantine before rollout; [566](https://github.com/vamseeachanta/deckhand/issues/566) and [579](https://github.com/vamseeachanta/deckhand/issues/579): queue/runtime reconciliation.

## Verified software evidence

- Final local scope suite: **178 passed in 19.36 seconds**; legal scan passed. Earlier focused suites overlap this total. Hosted CI remains a separate source of truth.
- Corpus: **94 paths**, 91 direct generations plus two jumper adapter generations, and one passing-ship own-schema case whose generation integration remains unknown. Three direct-schema rejections remain visible.
- **534 generated files:** 93 change only the implicit General `RestartStateRecordingTest` from tilde to quoted empty; 441 are byte-identical. No unexpected generated changes. Explicit generic overrides retain their values.
- Hash seed was pinned to zero. Initial unpinned ordering differences were preserved and routed to the existing follow-on issue rather than normalized away.
- Template changes are comments only: single mooring line, regular-wave height and period. Parsed YAML is unchanged. Current source-template SHA-256 at this checkpoint: `1fa7c6879eca05511a330dfd042fec39cdf21ba65f0f82b1653810b464d43be6`.
- Offline source/reference comparison has **56 unresolved differences**. Reference compatibility is false; the original-reference route is blocked. Code/test success is not engineering equivalence.

## Native attempt — do not repeat automatically

The one candidate attempt used code `f0f35bd14d9d695948463606c3606fe7408426fa` at `2026-09-11T21:02:05Z`, Python 3.11.15 and OrcaFlex 11.6c. It failed at `api.Model(threadCount=1)` with `OrcFxAPI.DLLError` 25: licensed users reached (`-4,132`), missing StatFlex feature (`-5,412`), and no HASP fallback files.

Parent elapsed: **4.922 seconds**. Child exit: **1**. Timeout: **false**. Cleanup: **confirmed**. Construction attempts: **one**. Model loads and completed solves: **zero**. No `LoadData`, statics, dynamics, saved simulation or independent readback occurred. One thread was requested; no model existed to observe its actual thread count. No retry occurred.

The six-file bundle's manifest SHA-256 was `63cb2c70becb38d4634e854ee145688ff1bf30c9ef29716f50b2e78964e868f0`. Do not attach that identity to a newly generated bundle without verifying its bytes and run identity.

## Machine and artifact boundaries

Native execution belongs on an explicitly qualified licensed Windows host, in a working authorized logon context. The Linux machine is a producer/offline analysis host; SSH reachability does not establish OrcaFlex licence access, and a public-key SSH logon is not equivalent to the tested Windows context. Do not execute the solver on Linux or invent a new scheduler to bypass this boundary.

The original Windows workstation retains private evidence roots for: the 94-case generator audits; the candidate six-file bundle; native stdout/stderr and process-cleanup evidence; and raw generated/reference model material. Their absolute paths belong in the private operator handoff, not this public document. Repository source is portable; those private roots are **not presumed copied or reachable** on another machine. Obtain an authorized transfer and verify hashes, or prepare a new reviewed bundle and record new identities. Keep the original evidence intact.

## Next actionable checkpoint

1. Finish/verify the authorized merges and record exact integrated SHAs. Establish a clean isolated destination checkout and inspect the existing runtime without deployment changes.
2. Review licence availability and entitlement with the owner in the intended Windows execution context. Do not run a licence diagnostic or smoke test that constructs a native Model merely to check whether the previous failure cleared; it is another native attempt. Do not kill, displace or alter another user's job to obtain a seat.
3. Present one exact candidate continuation for authorization: reviewed source revision, verified bundle and contract, approved host/context, source stages **11.5 + 100 seconds**, **one thread**, **300-second execution deadline plus 10-second cleanup allowance**, expected artifacts and failure/cleanup behavior. Verify these limits against the final integrated CLI/contract before invocation; do not improvise arguments.
4. Only after that new checkpoint is explicitly approved, make one bounded candidate attempt through the reviewed local wrapper. Retain phase-specific evidence and fail closed. Do not shorten stages, relax tolerances, automatically retry, run the incompatible original reference, submit through Deckhand, modify tasks or activate deployment.
5. On licence failure, stop and record it. On model/load/solve failure after licence recovery, record the precise stage and plan the smallest regression-backed repair. On successful solve, verify independent saved-result readback and numerical outputs before reporting candidate qualification. Keep the 56 unresolved reference differences and engineering limits visible.

Installation is next only after the mooring checkpoint has an honest disposition. Reuse the existing audited installation representatives and model-generation/extraction code; do not claim arbitrary component FEA or end-to-end fleet coverage from this single case.

Before handing back, run the required cleanup audit and report CLEAN / EXPECTED / UNEXPECTED residue, exact integration state, evidence locations and the single next checkpoint. Preserve private evidence and unrelated dirty work. Do not announce operational qualification while native execution or engineering evidence remains incomplete.
