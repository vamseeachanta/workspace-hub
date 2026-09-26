# Plan for #3894: Solver-neutral simulation study workflow

> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3894
> **Status:** draft r4, 2026-09-25. r4 folds in an operational-lessons brief from the parallel CFD campaign session (§r3 → r4); it adds requirements to existing stages and changes no architecture. Before that, as r3: r2 revised r1 against the r1 review. r3 applies the r2 review findings (Claude MAJOR, Codex MAJOR) as inline patches, per the cross-review routing rule (no dispatched r3 review). The Agy lane failed both rounds from a local argv-limit defect (#3896), not an outage. The plan awaits owner approval. Nothing in this plan is implemented.
> **Client:** N/A. No client deliverable is in scope. One private client-wiki record, a CFD campaign review, was consulted, and it is summarised here without identifiers.
> **Project:** N/A
> **Lane:** Claude (orchestration and planning). Implementation lanes are assigned per wave after approval.
> **Review artifacts:** `scripts/review/results/2026-09-25-plan-3894-{claude,codex,gemini,disagreement}.md` (r1); r2 artifacts will be written beside them.
> **Complexity:** T3. The work is cross-repo (digitalmodel, deckhand, workspace-hub) and systemic.

## r1 → r2 disposition

| r1 finding | r2 change |
|---|---|
| Claude F1 (unembedded evidence) | The §Evidence block embeds command output for issue states, path existence, gap proofs and counts. |
| Claude F2 (`scripts/solver` queue unresolved) | Verified. The queue is registered but absent on ace-win-1. The plan adds a disposition: retire it, as a W3 precondition. |
| Claude F3 (ITTC constants lack a citation route) | W0b adds ITTC standards pages plus ledger/registry rows. Until they land, the constants carry `unsourced-approximate` and W2 is gated on them. The Fr_T band is re-attributed to Maki (2006), not ITTC. |
| Claude F4 (pilots assert only plumbing) | Pilot A requires a `measured` comparator and a `conservation` check. Pilot B requires `conservation` and `closed-form` checks. Tolerances are fixed in this plan. |
| Claude F5 (no comparator class; no stopping thresholds) | The schema requires `comparator.class` and rejects a study whose comparators are only `archived-run`/`none` unless the study is labelled `regression-only`. Stopping thresholds are required study fields. |
| Claude F6 (stationary oscillation burns the budget) | A stationary oscillation stops after N whole cycles, with U_i. |
| Claude F7 (stale `tri`) | The pseudocode reads the triage for each case from the ledger. |
| Claude F8 (guard undefined; tick scheduler unregistered) | `digitalmodel.study.guard` is defined as the sole writer of stop. The monitor runs inside the existing Deckhand agent loop, so no new scheduler surface is added. Any future scheduler entry must be registered in `mutation-surfaces.yaml`. |
| Claude F9 (approval-control change inside the plan) | The `policy.yml` standing-approval change is removed from scope. It becomes its own issue, gated on deckhand#551. |
| Claude F10 (merge written as a deliverable) | W1 depends on #3891 landing. Merging it is not work this plan performs. |
| Claude F11 (header fields) | Header fields and the Artifact Map rows for the plan, tests and reviews are added. |
| Claude F12 (skill duplication) | The skill disposition is explicit: extend the existing stage skills and add one index skill. `engineering/INDEX.md` is added to Files to Change. |
| Claude F13 (surface enforced at render time) | A commit-time path guard is added: public repos refuse `study.yml` with `surface ≠ public`. |
| Claude F14 (`run_record` fields) | `parallel_mode` and `platform` are added. |
| Claude F15 (vocabularies) | Three separate fields with fixed vocabularies are defined, plus a render test that PASS never appears in a verdict position. |
| Claude F16 (retrieval at plan time) | The drive-index search was run at plan time on ace-linux-1 (§Gaps). The deckhand checkout is verified current (0 behind origin). |
| Codex F1 (adapter path inconsistency) | All new modules live under `src/digitalmodel/study/`, including `adapters/`. |
| Codex F2 (wrong OrcaFlex path) | Corrected to `src/digitalmodel/orcaflex/batch_parametric.py`. |
| Codex F3 (queue schema migration) | Queue `REQUEST_SCHEMA` 1 → 2, with optional fields and backward-compatibility tests. |
| Codex F4 (data ownership) | Pilot results go to private `digitalmodel-data` with a manifest (dataset id, revision, SHA-256) and read-back. Public inputs are fixtures only. |
| Codex F5 (CI vs licensed host) | The acceptance criteria are split into per-repo CI suites and licensed-host evidence. |

## r2 → r3 disposition (inline patches)

| r2 finding | r3 change |
|---|---|
| Claude F1 (budget stop unreachable; classes without an action) | The budget is evaluated first. Every class has an explicit disposition. `stall_window` is a required stop threshold. Tests cover the stop decision per class (Test 3b). |
| Claude F2 (Pilot B conservation wrong for a grounded line) | Restated as a full vertical force balance including the seabed and anchor reactions. The closed-form catenary check uses a fully suspended fixture. |
| Claude F3 (undefined cards; hull, dataset and feasibility) | The hull, dataset, speeds and a feasibility fallback are named in §Acceptance. The dataset is added to W0b. The cards are listed in §Owner decisions. |
| Claude F4–F6, Codex F5 (`SolverQueue` retirement) | Retirement is **removed from this plan** and becomes its own issue, which must enumerate the mutator file, the registry row and 30+ references. This plan needs only that new studies do not use it. Pilot B has a precondition: an operator-captured `Get-ScheduledTask -TaskName SolverQueue` output from ace-win-2 (the named evidence artifact). |
| Claude F7, Codex F3 (citation contradiction) | The ship path is struck. W2 cannot merge without W0b. There is no `unsourced-approximate` production path; the label exists only in test fixtures. |
| Claude F8 (undeclared deckhand → digitalmodel dependency) | The monitor and guard run inside the dispatched job (`digitalmodel.study.run_case` supervises its own solver). Deckhand only dispatches the standard `uv run python -m digitalmodel <input.yml>` command. There is no new Deckhand import or `pyproject` dependency. |
| Claude F9, Codex F1–F2 (surface vocabulary and enforcement) | The rule's vocabulary is adopted for `surface` (internal / client-deliverable / hosted), and a separate `residency` field is added (public-repo / client-wiki / private-data). The guard is vendored into digitalmodel pre-commit and CI (the wiki-sibling precedent). It checks residency against repo visibility, runs the existing `scripts/legal/legal-sanity-scan.sh` deny-list over study files, and allowlists file types in public study directories. Limitation stated: it cannot prove the absence of every restricted payload. |
| Claude F10 (guard receipt) | Preflight requires `runTimeModifiable true`. The guard confirms the stop from the solver log (termination at the next write), not from the file write. |
| Claude F11 (conservation normalisation) | The water-volume check is normalised to hull displaced volume. |
| Claude F12 (S11 publication) | Any hosted or HF publication is a consequential action with its own approval. The pilots commit only to private `digitalmodel-data`. `report_pack` is verified present (`src/digitalmodel/report_pack/workflow.py`). |
| Claude F13 (throughput field) | `run_record` adds `wall_clock_s`, `cells_or_dof`, `steps` and `s_per_step`. |
| Claude F14 (skill paths) | Corrected to `.claude/skills/engineering/marine-offshore/...`. |
| Claude F15 (Agy degradation) | The cause is established: a controlled pair (20 KB rc=0 with output; 41 KB rc=126) shows a Windows argv-limit defect, filed as #3896. The review is recorded as two-provider consensus with a known third-lane defect, not a policy degradation. The owner decides whether to wait for #3896 (card G03). |
| Claude F16 (freshness) | The evidence script ran `git fetch -q origin` before each comparison; §Evidence now states this. |
| Claude F17 (Test 14 fixtures) | The fixtures are named per comparator. |
| Codex F4 (review-pack dependency) | W0a defines the card schema (JSON Schema v1) as the interface. W1 depends on #3892 approval, not on the #3891 rule merge. |

## r3 → r4: lessons from a multi-lane CFD campaign

Source: a brief from the session operating a client hull-resistance campaign (11 conditions × 3 speeds; interFoam with local time stepping; five lanes of 60/20/14/14/8 ranks; two OpenFOAM versions). It is summarised here without identifiers. Each lesson maps to a stage and a test.

| # | Lesson | Plan element | Test |
|---|---|---|---|
| L1 | **Stage early, launch late.** Everything that can fail runs before the handoff: checkpoint complete on every rank, stale markers archived (not deleted), controls edited, run config written, guard preflight `--check-only` passed. The unattended step only launches. | S3 preflight gains a `stage()` phase. S4 launch is a separate, trivial step. | 16 |
| L2 | **Idempotent launch contract:** launch only when the solver count on the lane is 0 AND the predecessor reached its target. Refuse a busy lane, a held lock, or a case that already carries a log. | Deckhand dispatch preconditions (W3) | 17 |
| L3 | **Measured lane speed drives the critical path.** Lanes differed 6× on the same case type; moving the critical-path job cut the finish by about 2.5 days. | `select_host()` ranks eligible hosts by measured `s_per_step` from prior `run_record`s for the same profile. | 18 |
| L4 | **Cross-host moves:** static files are pre-staged; only the checkpoint is copied at switchover; SHA-256 manifests are sorted with `LC_ALL=C`; a restart-in-place fallback is always carried. | S6 continuation carries a transfer receipt (source and target `host:/path`, per-rank digests, fallback). | 19 |
| L5 | **Remote-exec hygiene:** `pgrep -c … \|\| echo 0` prints two lines; `pgrep -f`/`pkill -f` self-match and hang on hosts with D-state processes, so use `pgrep -x` plus `/proc/<pid>/stat`; `set -u` breaks vendor environment scripts; scripts piped from Windows carry CRLF, and a relay hop expands `$`, so send base64 and decode on the target. | One shared remote-exec helper in `digitalmodel.study.hosts`; no ad-hoc shell in adapters. | 20 |
| L6 | **Receipts name the parent with its host** (`host:/path`). An unprefixed path resolves on the child host and fails silently. | `run_record` checkpoint-chain entries are `host:/path` and validated. | 6 (extended) |
| L7 | **In-place continuations rewrite the configured start.** The chain start is taken from the force/log history, not the run config. Provenance-tool changes are regression-tested against the ledger's recorded inputs, labelled `archived-run`. | S7 provenance | 6 (extended) |
| L8 | **Caches need a freshness key.** Cache only finished runs, keyed to the end marker; never cache an empty read. | The reducer's block cache | 4 (extended) |
| L9 | **Mid-run cells are held at their last published value.** One cell's verdict flipped three times mid-run, and another's mean moved by more than its U_i between the mid-run and final readings. | S11: only finished runs publish; the ledger carries the last published value with its date. | 21 |
| L10 | **Nothing is deployed to `/tmp`.** Helpers are redeployed with a hash check, and an empty read is an error. | Host helpers live in the job's work root with a digest check | 20 |
| L11 | **Probe the GPU driver after any reboot before an MPI launch** (background `nvidia-smi`, 10 s). A hung driver froze every MPI start-up, and CPU solvers ran more than 25× slower until reset. | The health gate's GPU probe is specified exactly so. | 10 |
| L12 | **Read the authoritative record** (result file, stop receipts, every case of a condition across lanes) before declaring a failure. | The reducer assembles the whole verified chain per condition; there is no single-case verdict. | 6 (extended) |
| L13 | **Convergence classes:** settled (U_i ≤ 5 %), wide (5–15 %), not bounded (amplitude grows every cycle; carry the mean, state no U_i), not assessable (fewer than 3 cycles past an adaptive transient floor with a mean-invariance test). | `result.json` `convergence` values; the thresholds are default study-spec values, overridable per study before the run. | 3 |
| L14 | **Bounded judgement for conditions a steady method cannot settle, without more compute** (restated after a correction from the source session). (a) The **primary bound** is interpolation from settled neighbours in speed, trim and draft. (b) Form-factor decomposition and Holtrop–Mennen-type estimators are **admissible as bounds only after a campaign-specific check** shows (1+k) ≥ 1, a non-negative implied wave coefficient C_W, and a stated Holtrop-vs-CFD gap. Otherwise they are reported as independent references alongside their disagreement, never as bounds. (c) A bound never replaces a result. A time-accurate pilot on one condition tests whether the defensible value falls inside the bound. | New reducer output `bound` for `not bounded` cases. It carries the interpolation estimator plus any admitted estimators, each a named comparator; non-admitted estimators are listed under `references` with the reason. **Why the gate exists:** in the source campaign, double-body runs returned (1+k) = 0.948–1.012, below 1 and therefore without a valid viscous/residuary split. The CFD viscous force sat below ITTC-57 in every cell (C_V/C_F57 = 0.85–0.93). Holtrop's k made the implied C_W negative on 7 of 10 conditions, and Holtrop totals ran up to 17.5 % above CFD at one draft with stern trim. Neither route was admissible there. The Holtrop–Mennen constants route through the citation contract (W0b). | 22 |
| L16 | **A detached remote launch must return.** A launch line of the form `cd X && setsid nohup cmd > log &` hung a cross-host orchestrator for 10 h although the launch succeeded. The `&&` list ran in a forked subshell that waited on `cmd` while still holding the caller's stdout; only `cmd` carried the redirect. Required form: `cd X` on its own line, then `setsid nohup cmd > log 2>&1 < /dev/null &`. **Corollary:** before stopping a stuck controller, confirm its failure fallback cannot launch a duplicate run; stop the controller by PID first, then its hung child. | The `digitalmodel.study.hosts` launch helper emits only the required form. The controller-stop procedure is in the operator skill. | 24 |
| L15 | **Documentation discipline:** corrections to issued documents are struck through and dated, never deleted; workbook notes are generated from data, dated to the method change; subagent writes are verified on disk before they are trusted. | S11 `report_pack` conventions; implementation-lane rule | 23 |

## Resource Intelligence Summary

### Existing repo code

The paths below were verified against `digitalmodel` `origin/main` 9468b119 and `deckhand` `origin/main` ea24989; see §Evidence.

- **Case generation exists for every major solver.**
  - OpenFOAM: `solvers/openfoam/case_builder.py`, `case_definition.py`, `parametric.py` (50 test files).
  - OrcaFlex: `solvers/orcaflex/modular_generator/schema/campaign.py` and `orcaflex/batch_parametric.py` (111 test files under `tests/solvers/orcaflex`).
  - Diffraction: `hydrodynamics/diffraction/spec_converter.py` and `parametric_spec_generator.py` (109 test files).
  - ANSYS: `ansys/apdl_generator.py` and `batch_runner.py` (18 test files).
  - The hull-resistance CFD module `solvers/openfoam/hull_case.py` is **absent on main**. It lives on an unmerged feature branch.
- **A partial unified coordinator exists:** `structural/parametric_coordinator.py` (WRK-256). It dispatches Cartesian sweeps for wall thickness, fatigue and OrcaFlex campaigns and aggregates them into one report. It has no CFD, diffraction or ANSYS path, and no provenance, monitoring or review stage. W0 decides its disposition (wrap it or subsume it; see card A08).
- **Dispatch.** The Deckhand licensed-run lane is the tested dispatcher.
  - `deckhand/src/deckhand/licensed_run_queue.py` uses `REQUEST_SCHEMA = 1`, and `validate_request` is at line 204.
  - `config/deckhand/policy.yml` allowlists 5 workflows.
  - The predecessor queue `workspace-hub/scripts/solver/` (process-queue, retry handler) was last changed 2026-06-15. It is registered as `local-windows-task-scheduler-solver-queue` in `config/scheduled-tasks/mutation-surfaces.yaml`:192-205. The `SolverQueue` task is **not installed on ace-win-1**. Its presence on ace-win-2 is not verifiable from here (RDP-only host).
- **Registry drift is confirmed.** `aqwa-diffraction-solve`, `openfoam-run-batch` and `solver-smoke-test` are allowlisted in `policy.yml` but have no row in `docs/registry/workflows.yaml`.
- **Continuation.** Inside `workflows/openfoam_run_batch.py` it is `set_start_from_latest_time`, with a per-case `_result.json` bound to `openfoam_batch_identity.py` `RunIdentity`. Continuation classification and whole-cycle reduction exist only in client-project scripts.
- **Monitoring.** OrcaFlex has `solvers/orcaflex/run_state.py`, and ANSYS has `ansys/results_extractor.py`. AQWA `.LIS` parsing exists in 3 copies:
  - `hydrodynamics/aqwa/aqwa_lis_files.py`
  - `hydrodynamics/diffraction/aqwa_lis_parser.py`
  - `marine_ops/marine_analysis/parsers/aqwa_lis_parser.py`
- **Provenance** exists in three forms:
  - `workflow_api/provenance.py` (`ResultEnvelope`)
  - OpenFOAM `RunIdentity`
  - project-local `case_provenance.json`
- **Verdict contracts.** `run_contract.py` defines PASS/WARNING/SKIPPED/FAIL/ERROR. Cross-solver comparison lives in `hydrodynamics/diffraction/multi_solver_comparator.py` and `cross_solver_acceptance.py`.
- **Review.** The review-pack generator prototype is held outside any repo (#3892). The physical-realism rule is draft PR #3891.
- **Skills.** Existing skills this plan extends and does not duplicate:
  - `.claude/skills/engineering/cfd/openfoam/analysis/stages/stage-01…06` (staged CFD workflow)
  - `.claude/skills/engineering/marine-offshore/orcaflex/batch-manager`
  - `.claude/skills/engineering/marine-offshore/aqwa/batch-execution`
  - `.claude/skills/engineering/marine-offshore/solver-benchmark`

### Standards

- **ITTC 7.5-03-02-03 (2014)**, practical guidelines for ship CFD applications (https://www.ittc.info/media/8165/75-03-02-03.pdf). §3.6: Δt < 0.01 L/U for one- and two-equation turbulence models; at least 20 steps per period for unsteady phenomena, "e.g. wetted transom instabilities". §3.8: oscillatory convergence.
- **ITTC 7.5-03-02-04 (2024 revision)**, resistance CFD (https://www.ittc.info/media/11960/75-03-02-04.pdf). Sinkage and trim are part of the solution; forces, trim and sinkage are to be monitored.
- **ITTC 7.5-03-01-01**, uncertainty analysis in CFD. For a stationary oscillation, U_i = (S_U − S_L)/2.
- **Maki (2006)**, transom-stern regimes (thesis, deepblue.lib.umich.edu/handle/2027.42/125702). It is the source of the 1 < Fr_T < ≈2.5 shedding band. This source is **not ITTC**, and r1's attribution is withdrawn.
- **Citation status.**
  - None of these has an entry in `data/document-index/standards-transfer-ledger.yaml` or `data/design-codes/code-registry.yaml` (0 matches, r1 review retrieval), nor a tracked wiki standards page.
  - Per `calc-citation-contract.md`, W0b creates them before any constant is coded. W2 cannot merge without them. There is no fail-open path: the `unsourced-approximate` label exists only in test fixtures.

### LLM Wiki pages consulted

- Generic engineering wiki: the interFoam free-surface convergence page. Its §6.3 cost table is internally inconsistent, as recorded in the source campaign's divergence note.
- Private client wiki (one campaign; not named in this public plan): a divergence engineering note and a workflow review, both dated 2026-09-21/25.

### Documents consulted

- Rules: `reproducibility-is-not-correctness.md`, `mechanism-before-publication.md`, `report-audience-and-surface.md`, `calc-citation-contract.md`, `scheduler-mutation-safety.md`, `merge-authorization.md`, `wiki-sibling-routing.md`, `engineering-register.md`.
- `docs/architecture/agent-data-handling-contract.md`: data ownership, manifests, read-back.
- Literature on routine resistance CFD:
  - Gatin, Vukčević & Jasak (2019), automated full-scale resistance: about 40 min of human time per ship; 1.1–1.4 h on 64 cores.
  - Ge & Bensow (NuTTS 2017), interface schemes on KCS.
  - Jasak, OceanFOAM 2015 lecture: wet-stern force drift "also in other codes".

### Gaps identified

- **Drive-index search**, run 2026-09-25 on ace-linux-1 with queries "simulation workflow", "CFD convergence", "ship resistance" and "OrcaFlex batch":
  - The CAD and knowledge indexes were reachable. `master_document_index` and `dde_literature_catalog` were unreachable from the shipped copy.
  - Hits were CAD files and vendor training material only. **No drive document bears on workflow design.** Hit paths are omitted here because several sit under client project folders.
- ITTC and Maki citation targets do not exist yet (see Standards).
- A measured cross-host throughput baseline exists for one CFD lane only.
- The status of the `SolverQueue` task on ace-win-2 is unverified.

### Evidence (embedded verification)

Commands were run 2026-09-25 from the Windows workspace, each comparison after `git fetch -q origin`; output is abridged.

```text
# issue states (gh issue view)
workspace-hub#3891 OPEN  Rule: physical realism review before a mechanism enters a report   (draft PR)
workspace-hub#3892 OPEN  feat(engineering): standard human-review pack ...
workspace-hub#3839 OPEN  fix(digitalmodel/fatigue): two of four rainflow paths understate stress range ...
deckhand#551       OPEN  design(licensed-run): standing approval for continuous sweep-family dispatch — owner decision
digitalmodel#943   CLOSED Parametrics plan: systematic sweeps over prepared use-cases -> atlases + lane dispatch
digitalmodel#938   OPEN  EPIC: Solver run preparedness
digitalmodel#1565  CLOSED openfoam_run_batch: default work/output dirs ...
digitalmodel#2051  OPEN  fix(orcaflex): preserve solver YAML defaults and fail closed on batch errors

# freshness
digitalmodel origin/main 9468b119
deckhand local HEAD ea24989 2026-08-01 == origin/main ea24989; rev-list HEAD..origin/main = 0

# git cat-file -e origin/main:<path>   (digitalmodel)
OK solvers/openfoam/{case_builder,case_definition,parametric}.py
OK solvers/orcaflex/modular_generator/schema/campaign.py   OK orcaflex/batch_parametric.py
OK hydrodynamics/diffraction/{spec_converter,parametric_spec_generator,multi_solver_comparator,cross_solver_acceptance}.py
OK ansys/{apdl_generator,batch_runner,results_extractor}.py
OK workflows/{openfoam_run_batch,openfoam_batch_identity}.py  OK solvers/orcaflex/run_state.py
OK workflow_api/provenance.py  OK run_contract.py  OK docs/registry/workflows.yaml
ABSENT solvers/openfoam/hull_case.py      ABSENT study/__init__.py

# test files (git ls-tree origin/main | test_*.py)
tests/solvers/openfoam 50 | tests/solvers/orcaflex 111 | tests/hydrodynamics/diffraction 109 | tests/ansys 18

# study-schema gap: git grep -E 'class +(Study|SimulationStudy|StudySpec)\b' origin/main -- src
src/digitalmodel/structural/parametric_coordinator.py     (only hit; WRK-256 coordinator, see above)

# deckhand queue schema
src/deckhand/licensed_run_queue.py:19: REQUEST_SCHEMA = 1
src/deckhand/licensed_run_queue.py:204: def validate_request(...)

# registry drift (policy.yml allowlist vs workflows.yaml)
aqwa-diffraction-solve False | openfoam-run-batch False | solver-smoke-test False
orcawave-diffraction-solve True | orcaflex-strength-post True

# predecessor queue
scripts/solver last commit b47a223ce 2026-06-15
mutation-surfaces.yaml:192-205 local-windows-task-scheduler-solver-queue (TaskName "SolverQueue")
Get-ScheduledTask on ace-win-1: no SolverQueue task present
```

## Artifact Map

| Stage | Canonical artifact | Owner module (proposed) |
|---|---|---|
| S0 Study spec | `study.yml`. Contents: matrix, method profiles, acceptance-rule version, comparators (class, tolerance), stopping thresholds (`min_cycles`, `max_growth_ratio`, `stall_window`, `budget`), `surface` (internal / client-deliverable / hosted), `residency` (public-repo / client-wiki / private-data), data destination | `digitalmodel.study.schema` |
| S1 Triage | `triage.json`: regime and method profile per case, with reasons and citations | adapter `triage()` |
| S2 Generate | case directory plus `case_manifest.json` (input digests, generator commit) | adapter `generate()` wrapping the existing builders |
| S3 Preflight | `preflight.json`: conservation checks before the run, plus mesh gates and a licence/host probe | adapter `preflight()`, `solvers/smoke` |
| S4 Dispatch | Deckhand queue request, schema 2 (`study_id`, `case_digest`) | deckhand |
| S5 Monitor/stop | `monitor.jsonl`, with class ∈ {converged, oscillating_stationary, growing, stalled, failed}. Runs inside the dispatched job (`digitalmodel.study.run_case` supervises its solver); no Deckhand import. | `digitalmodel.study.monitor` plus adapter `parse_log()` |
| S5' Guard | stop request written only by the guard. OpenFOAM: `stopAt writeNow` via `foamDictionary`, with `runTimeModifiable true` required at preflight. The stop is confirmed from the solver log showing termination at the next write, not from the file write. OrcaFlex: none. | `digitalmodel.study.guard` |
| S6 Continue | continuation request carrying `checkpoint_digest` (queue schema 2) | deckhand |
| S7 Provenance | `run_record.json`: solver, version, argv, host label, ranks, `parallel_mode`, `platform`, code commit, input digests, checkpoint chain to cold origin, `wall_clock_s`, `cells_or_dof`, `steps`, `s_per_step` | `digitalmodel.study.provenance` |
| S8 Reduce | `result.json`: value, uncertainty, `execution`, `convergence` (settled / wide / not_bounded / not_assessable), `checks[].verdict`, and for `not_bounded` a `bound` with its estimators (L14) | `digitalmodel.study.reduce` |
| S9 Render | standard figure set per case | adapter `render()` |
| S10 Review | review-pack HTML plus reviewer JSON; `acceptance` is set only from reviewer JSON | `scripts/review/review_pack.py` (#3892) |
| S11 Issue | accepted cases only, into workbook, report or dataset; data to its owner repo with a manifest. Hosted or HF publication is a separate consequential action with its own approval. | `report_pack` (`src/digitalmodel/report_pack/workflow.py`, verified present); hf-dataset-publishing only under separate approval |
| Ledger | `study_state.json` plus a generated status page | `digitalmodel.study.ledger` |
| Plan | this file | workspace-hub |
| Tests | `digitalmodel/tests/study/**`, `deckhand/tests/deckhand/test_licensed_run_queue_schema2.py`, `workspace-hub/tests/review/test_review_pack.py` | per repo |
| Reviews | `scripts/review/results/2026-09-25-plan-3894-*` | workspace-hub |

**Vocabularies.** These are fixed and are never interchanged:

| Field | Values | Set by |
|---|---|---|
| `execution` | PASS / WARNING / SKIPPED / FAIL / ERROR (existing `run_contract.py`) | Records whether the solver ran. Never rendered in a physics-verdict position. |
| `checks[].verdict` | implausible / not_implausible / not_evaluated | Physics against its comparator. |
| `acceptance` | pending / accepted / accepted_with_note / queried / rejected | Reviewer JSON only; no code path sets it. |

## Deliverable

1. **`digitalmodel.study`**, under `src/digitalmodel/study/`: schema, ledger, monitor, guard, provenance, reduce, and `adapters/{base,openfoam,orcaflex}.py`; diffraction and ANSYS adapters follow in W5.
2. **Deckhand**:
   - queue schema 2, with optional `study_id`, `case_digest` and `checkpoint_digest`; v1 requests remain valid;
   - continuation request handling;
   - a host health gate: disk-free threshold, GPU probe with timeout, licence probe, rank count;
   - a registry-drift test.
3. **Dependent items:**
   - review pack promoted to `scripts/review/` (#3892) against the W0a card schema;
   - ITTC and Maki standards pages, the Pilot A measured dataset catalog entry, and ledger and registry rows (W0b);
   - the `check-study-surface` guard, vendored into digitalmodel pre-commit and CI.
4. **Pilots A and B**, run end to end with correctness comparators. Results go to private `digitalmodel-data` with a manifest.
5. **Out of scope:**
   - changing the standing-approval policy (a separate issue, gated on deckhand#551);
   - `SolverQueue` retirement (a separate issue that must enumerate the mutator, the registry row and 30+ references);
   - any hosted or HF publication;
   - migrating any client campaign in flight;
   - rewriting generators.

## Pseudocode

```text
study = load_study("study.yml")            # schema: rule version, comparators w/ class+tolerance, stop thresholds, surface
for case in study.matrix():
    ledger.record(case, stage="triaged", triage=adapter.triage(case))      # per-case, persisted

for case in ledger.cases(stage="triaged"):
    tri = ledger.triage(case)                                               # read per case (r1 F7)
    d = adapter.generate(case, tri.profile)
    pre = adapter.preflight(d)                                              # conservation before run
    if pre.failed: ledger.hold(case, pre); continue
    host = select_host(health_gate=True)                                    # skip + record ineligible hosts
    deckhand.enqueue(schema=2, study_id=study.id, case_digest=d.digest, host=host)

# run_case: the dispatched job supervises its own solver (no Deckhand import, no scheduler surface)
def run_case(case):
    tri = ledger.triage(case)
    proc = adapter.launch(case)
    while proc.alive():
        sleep(study.stop.tick_s)
        s = adapter.parse_log(case)                 # raises on empty/CRLF/stale-sibling reads
        if budget_exhausted(case):                  # evaluated FIRST (r2 F1)
            guard.request_stop(case, reason="budget"); continue
        cls = monitor.classify(s, study.stop)       # phase-marker cycles; stall_window; max_growth_ratio
        match cls:
            "converged":              guard.request_stop(case, reason="converged")
            "oscillating_stationary": if cycles(s) >= study.stop.min_cycles: guard.request_stop(case, reason="stationary")
            "growing":                if tri.profile.steady:
                                          ledger.flag(case, "method mismatch: re-triage"); guard.request_stop(case, reason="growing-steady")
                                      # unsteady profile: keep running; budget bounds it
            "stalled":                guard.request_stop(case, reason="stalled"); ledger.flag(case, "stalled")
            "failed":                 proc.terminate(); ledger.hold(case, "failed")
    guard.confirm_stop_from_log(case)               # termination at next write seen in the solver log

on run_end(case):
    rec = provenance.record(case)                    # chain to cold origin, link by link
    if rec.needs_continuation: deckhand.enqueue(schema=2, checkpoint_digest=rec.checkpoint)
    else:
        res = reduce(case, study.rule_version)       # execution / convergence / checks[].verdict
        review_pack.add_card(case, res, adapter.render(case))

on reviewer_json(file): ledger.apply_acceptance(file)   # the only writer of `acceptance`
issue(study) -> only acceptance in {accepted, accepted_with_note}
```

## Files to Change

The paths below are created or changed after approval; nothing is implemented yet.

- **digitalmodel:**
  - new: `src/digitalmodel/study/{__init__,schema,ledger,monitor,guard,provenance,reduce,run_case,hosts,bounds}.py`;
  - existing: `.pre-commit-config.yaml` and `.github/workflows/quality-gates.yml` (vendored `check-study-surface` hook);
  - new: `src/digitalmodel/study/adapters/{__init__,base,openfoam,orcaflex}.py` (W2) and `{diffraction,ansys}.py` (W5);
  - new: `tests/study/**`;
  - existing: `docs/registry/workflows.yaml` (3 missing rows);
  - existing: `structural/parametric_coordinator.py` (per card A08).
- **deckhand:**
  - existing: `src/deckhand/licensed_run_queue.py` (schema 2), `licensed_run_agent_runtime.py` (health gate, continuation; no digitalmodel import);
  - new: `tests/deckhand/test_licensed_run_queue_schema2.py`, `test_licensed_run_health_gate.py`.
- **workspace-hub:**
  - new: `scripts/review/review_pack.py` plus `tests/review/test_review_pack.py` (#3892, after #3891 lands);
  - new: `scripts/enforcement/check-study-surface.sh` plus tests (commit-time guard);
  - existing: `.claude/skills/engineering/cfd/openfoam/analysis/stages/*`, `.claude/skills/engineering/marine-offshore/orcaflex/batch-manager/SKILL.md`, `.claude/skills/engineering/INDEX.md` (links to the workflow);
  - new: `.claude/skills/engineering/simulation-study/SKILL.md` (index skill that points to the stage skills, not a copy);
  - no change to `scripts/solver/` or `mutation-surfaces.yaml` in this plan (retirement is a separate issue);
  - this plan.
- **llm-wiki (generic, private):** new ITTC 7.5-03-02-03, 7.5-03-02-04 and 7.5-03-01-01 standards pages, plus a Maki (2006) methodology page with citation frontmatter (W0b).
- **workspace-hub data:** `standards-transfer-ledger.yaml` and `data/design-codes/code-registry.yaml` rows (W0b).
- **digitalmodel-data (private):** the pilot dataset directories with manifests (W4).

## TDD Test List

1. **Schema.** A spec is rejected if it lacks any of the following: rule version, `comparator.class`, a tolerance, stop thresholds (`min_cycles`, `max_growth_ratio`, `stall_window`, `budget`, `tick_s`), a `surface` in {internal, client-deliverable, hosted}, a `residency` in {public-repo, client-wiki, private-data}, or a data destination. A spec whose comparators are all `archived-run`/`none` is rejected unless it is labelled `regression-only`.
2. **Rule versioning.** Changing the rule of a running study requires a version bump. Cases already reduced keep their version; no retroactive rewrite.
3. **Monitor**, on synthetic series with cycles delimited by phase markers:
   - a decaying series is classed converged;
   - a stationary series is classed oscillating_stationary, with U_i equal to the half-range, and a stop is requested after `min_cycles`;
   - a rising envelope is classed growing, and U_i is refused;
   - a flat stalled series is classed stalled;
   - a variable-period series is not mis-phased.
3b. **Stop decision per class.** Budget exhausted with any class → stop. Converged → stop. Stationary at `min_cycles` → stop. Growing with a steady profile → flag and stop. Growing with an unsteady profile → continue. Stalled → stop and flag. Failed → terminate and hold. No class leaves a case running past its budget.
4. **Monitor input faults.** CRLF, stale sibling file, empty read and mid-write file each raise. None yields an empty-valid series. These regress three defects from the source campaign.
5. **Guard.** It is the only module that writes stop. A second writer is refused. The stop is written atomically, with a receipt. Preflight refuses an OpenFOAM case without `runTimeModifiable true`. `confirm_stop_from_log` fails when the solver log shows no termination at the next write within one write interval.
6. **Provenance.** A chain with a missing link, or a rank change without a transfer receipt, is refused. All run-configuration fields are present: solver, version, argv, host, ranks, `parallel_mode`, `platform`, commit, digests.
7. **OpenFOAM triage** on STL fixtures of known immersion:
   - dry transom → LTS;
   - wetted transom with 1 < Fr_T < 2.5 → time-accurate;
   - the Fr_T band constant emits its Maki (2006) Citation sidecar, and resolution fails closed if the W0b page is absent.
8. **OrcaFlex adapter.**
   - Δt is set from the shortest natural period.
   - Preflight flags an applied-load resultant more than 1.0 % off target.
   - The vertical force balance (Σ end vertical reactions + seabed reaction = total submerged weight + applied vertical loads) is checked on a grounded-line fixture.
   - The closed-form catenary is checked on a fully suspended single-line fixture.
9. **Deckhand queue.**
   - Schema-1 requests still validate.
   - Schema-2 requests with the new optional fields validate.
   - A mixed v1/v2 queue drains in order.
   - A continuation whose checkpoint digest mismatches is held; no cold start.
10. **Deckhand health gate.** A full disk, a GPU probe over its timeout, or a missing licence makes the host ineligible, and the reason is recorded.
11. **Registry drift.** A `policy.yml` allowlist entry without a `workflows.yaml` row fails.
12. **Vocabularies.** The rendered review pack and report never place `execution` values in a verdict position. `acceptance` has no writer other than the reviewer-JSON ingest.
13. **Surface guard.** Vendored into digitalmodel pre-commit and CI:
    - In a repo whose visibility is public, it refuses a `study.yml` with `residency` ≠ public-repo.
    - It runs the `.legal-deny-list.yaml` scan over study directories.
    - It refuses file types outside the public study allowlist (`.yml`, `.json`, `.md`, `.py`, plus named fixtures).
    - It passes the public pilots.
    - Stated limitation: it cannot prove the absence of every restricted payload.
14. **Check qualification**, on named fixtures where the expectation must hold, before a comparator may flag another case:
    - wake wavelength on the dry-transom public hull case (within 2.5 % of 2πU²/g);
    - vertical force balance on a grounded-line OrcaFlex fixture (±1.0 %);
    - catenary on a fully suspended line (±2.0 %);
    - VOF water-volume check on a hydrostatic box of known displacement (Archimedes; within 0.1 % of the box displacement).
15. **Data read-back.** The pilot manifest SHA-256 values match the stored files on re-read.
16. **Stage/launch split.** `stage()` runs every fallible step and records a receipt. `launch()` refuses to run without a matching stage receipt and performs no fallible preparation.
17. **Idempotent launch.** A second launch on a busy lane, a held lock, a case that already has a log, or a predecessor short of its target is refused. A double fire leaves exactly one solver.
18. **Throughput-ranked host selection.** Given recorded `s_per_step` per host and profile, `select_host` picks the fastest eligible host. A host without a record ranks last and is flagged, never excluded silently.
19. **Transfer receipt.** A checkpoint move records source and target `host:/path` and per-rank SHA-256 values sorted under `LC_ALL=C`, verified on the target. A digest mismatch holds and falls back to restart-in-place.
20. **Remote-exec helper.** Fixtures cover: payloads with CRLF, `$` in content sent across a relay (base64 round-trip), a `pgrep -x` count returned as one integer, vendor env sourced without `set -u`, and a helper whose digest mismatches (refused).
21. **Mid-run hold.** A running case never updates the published value. The ledger returns the last published value with its date until the run ends.
22. **Bound for not-bounded cases.**
    - Interpolation from settled neighbours is the primary estimator. With fewer than two settled neighbours on an axis, it reports `not_evaluated` for that axis.
    - A form-factor or Holtrop-type estimator enters `bound` only if the campaign check passes: (1+k) ≥ 1, implied C_W ≥ 0 in every cell used, and the Holtrop-vs-CFD gap stated. Fixture: a campaign with (1+k) = 0.95 and negative C_W puts both estimators under `references`, each with its reason.
    - The bound is labelled as a bound, never as a result or with U_i.
24. **Launcher returns.** Each launch path is invoked through `ssh host '…'` and through `$( … )`, with a solver stub that sleeps for 600 s. The call must return within 10 s, leaving the stub running and its output in the log. A regression fixture of the `cd X && setsid nohup cmd > log &` form must fail this test. A second test stops a controller stub in the prescribed order and asserts that no duplicate launch occurs.
23. **Corrections.** A regenerated report that changes an issued value renders the old value struck through with the correction date. A hand-edited generated note fails the regeneration check.

## Acceptance Criteria

**Per-repo CI** (ordinary runners, no licence):
- digitalmodel `tests/study/**` green;
- deckhand `tests/deckhand/test_licensed_run_*` green, including schema 2;
- workspace-hub `tests/review/**` and `check-study-surface` green.

**Pilot A: OpenFOAM, public hull**, on an enrolled Linux lane via Deckhand:
- **Hull and data:** DTC, the Duisburg Test Case (the geometry of the OpenFOAM `DTCHull` tutorial), against the published calm-water model-test resistance (el Moctar, Shigunov & Zorn, 2012). The dataset is catalogued in W0b with source, edition and digest.
- **Speeds:** at least 6 cases across the published range.
- **Feasibility of the time-accurate criterion:**
  - W0a measures transom immersion on the tutorial geometry with the existing transom tool, and records Fr_T per test speed.
  - If a tested speed falls in 1 < Fr_T < 2.5, that case is triaged time-accurate.
  - If none does, the criterion is replaced by one forced comparison case run both ways (LTS and time-accurate), whose means agree within their combined U_i.
  - Whether the DTC transom is wetted at the tested speeds is **not established** in this plan.
- **Measured comparator:** total resistance coefficient within **±5 %** of the published model-test value at each speed tested.
- **Conservation:** water-phase volume change over the reduction window of **≤ 1.0 % of the hull displaced volume**.
- Every stage artifact is present. The review pack is produced, reviewer JSON is ingested, and the result goes to `digitalmodel-data` with a manifest verified by read-back.

**Pilot B: OrcaFlex, public example**, on the licensed Windows lane via Deckhand:
- At least 4 cases.
- **Precondition:** an operator-captured `Get-ScheduledTask -TaskName SolverQueue` output from ace-win-2, stored with the pilot evidence, shows the task absent or disabled. This rules out seat contention.
- **Conservation:** static vertical force balance, Σ end vertical reactions + seabed reaction = total submerged weight + applied vertical loads, within **±1.0 %**.
- **Closed-form:** static catenary tension within **±2.0 %** for a fully suspended single-line case.
- Same artifact, review and data requirements as Pilot A.
- The licensed-host evidence is the Deckhand run records plus `run_record.json`, not CI.

**General:**
- No project-local controller is used in either pilot.
- One `run_record.json` schema covers both solvers, with documented mappings from `ResultEnvelope` and `RunIdentity`.
- The generated status page shows stage, host and classification per case without manual editing.
- Code-stage cross-review is clean.

## Adversarial Review Summary

| Round | Claude | Codex | Agy | Outcome |
|---|---|---|---|---|
| r1 | MAJOR (16 findings, 7 blockers) | MAJOR (5 findings, all blockers) | UNAVAILABLE (empty output, rc=0) | Revised to r2; all 21 findings dispositioned above |
| r2 | MAJOR (17 findings, 8 blockers) | MAJOR (5 findings, all blockers) | no output (#3896) | r3 inline patches; all 22 findings dispositioned above |

**Agy.** Agy produced no review in either round. The cause is established by a controlled pair: 20 KB rc=0 with output, 41 KB rc=126. A Windows argv limit sits below the wrapper's Linux-sized cap. It is filed as #3896. This is a local defect, not a provider outage. The owner decides (card G03) whether to accept two-provider consensus after r3 or to wait for #3896 and re-run Agy.

## Risks and Open Questions

1. **Scope creep into generators.** Adapters wrap the existing builders. A generator change files its own issue.
2. **Standing approval (deckhand#551).** It is out of scope here. The pilots run under per-run approval, which is slower.
3. **`SolverQueue` on ace-win-2.** It is unverified. Retirement is out of scope. Pilot B carries the evidence precondition.
4. **Linux lanes.** Only gpu-claw is onboarded as a Deckhand Linux execution host. Enrolment follows `onboard-gpu-claw-cfd-host.md`, per card A07.
5. **Client campaigns.** They adopt the workflow at their next study, or by explicit owner decision. None is migrated mid-flight.
6. **Public/private split.**
   - Code and public-pilot *inputs* are public.
   - Solver *results* go to private `digitalmodel-data` per the data-handling contract.
   - Client studies live in client wikis.
   - The commit-time guard catches residency and deny-list violations. It cannot prove that no restricted payload exists, so client-study review remains a human gate.
7. **Citation dependency.** W2 cannot merge until W0b lands the standards pages. If W0b stalls, W2 stalls; there is no fail-open path.
8. **Throughput.** It is unknown across hosts. The pilots record throughput per host in `run_record.json`, which becomes the first cross-host baseline.

### Waves (child issues filed after approval)

| Wave | Content | Depends on |
|---|---|---|
| W0a | Schemas: `study.yml`, `case_manifest`, `run_record`, `result`, ledger, vocabularies, review card JSON Schema v1; `parametric_coordinator` disposition; DTC transom Fr_T measurement | — |
| W0b | ITTC, Maki and Holtrop–Mennen standards/method pages, DTC measured-dataset catalog entry, ledger and registry rows | — |
| W1 | Review pack promoted to `scripts/review/` against the card schema | W0a; #3892 approved |
| W2 | Monitor, guard, reduce, run_case; OpenFOAM and OrcaFlex adapters; surface guard vendored into digitalmodel | W0a, W0b |
| W3 | Deckhand queue schema 2, continuation, health gate, registry drift | W0a |

## Owner decisions (decision board, local)

These cards are on the local decision board; they are listed here so the plan is self-contained.

| Card | Decision | Recommendation |
|---|---|---|
| G01 | Approve this plan | After the review converges |
| G02 | Sequencing of #3891 (rule) and #3892 (generator) | Rule first; generator in W1 |
| G03 | Two-provider consensus after r3, or wait for #3896 and re-run Agy | Accept two-provider r3; re-run Agy at the code stage |
| A01 | Where the study package lives | `digitalmodel.study` |
| A02 | Single dispatcher | Deckhand for all solvers |
| A03 | Standing-approval scope | Per study, digest-bound (implemented in the separate deckhand#551 issue) |
| A04 | Pilots | Public: DTC (OpenFOAM) and an OrcaFlex example |
| A05 | Acceptance-rule changes | Pinned per study; prospective only |
| A06 | Review pack vs decision board | Two page types on one card schema |
| A07 | Execution hosts | Windows lane, ace-linux-1 and gpu-claw; Spark after driver reset |
| A08 | Existing `parametric_coordinator` | Wrap now; migrate callers in W6 |
| W4 | Pilots A and B | W1–W3 |
| W5 | Diffraction and ANSYS adapters (ANSYS preflight reaction-sum) | W4 |
| W6 | Consolidation: one `.LIS` parser, one sweep abstraction (#938 epic), rainflow (#3839) | W4 |

## Complexity: T3
