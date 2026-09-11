# Plan: one OrcaFlex execution contract for local and remote producers

Issue: [#3831](https://github.com/vamseeachanta/workspace-hub/issues/3831)
Status: draft; revision 6; deployment will await runtime cleanup repair, queue preservation/recovery and scope/cutover approval
Complexity: T3 | Mode: parallel-readonly planning, isolated implementation lanes after approval
Client: N/A | Lane: lane:claude

## Deliverable

The ecosystem will provide one supported way to submit OrcaFlex work locally or from an enrolled machine, execute on the licensed Windows workstation, and retrieve trustworthy results. Deckhand will own dispatch and host execution; digitalmodel will own solver behaviour; workspace-hub will own the operational contract and coverage report. A local submit will use the same queue and credentialed agent as a remote submit.

## Resource Intelligence Summary

The implementation will use the separately recorded [discovery evidence](../reports/2026-09-09-orcaflex-execution-evidence.md) to distinguish deployed drift from missing upstream functionality. It will reuse the upstream smoke workflow, timeout handling, solver-root configuration, and queue reliability fixes. It will not reimplement those features.

Existing work will remain linked to [Deckhand production epic](https://github.com/vamseeachanta/deckhand/issues/572), [batch onboarding](https://github.com/vamseeachanta/deckhand/issues/550), [digitalmodel batch](https://github.com/vamseeachanta/digitalmodel/issues/1554), [result-return](https://github.com/vamseeachanta/deckhand/issues/564), and [dispatch surface](https://github.com/vamseeachanta/deckhand/issues/582). Identity changes will follow [the existing identity decision](https://github.com/vamseeachanta/deckhand/issues/581); this work will retain the currently deployed alias contract until a separately verified migration lands. It will not broaden the ANSYS-specific [neutral scope issue](https://github.com/vamseeachanta/deckhand/issues/543).

Engineering standards-derived constants will not be introduced. Drive-index results will be treated as incomplete: five registered indexes will need reachable mounts before they can supply evidence. Private machine mappings, credentials, and customer paths will stay in the private deployment tier. The public plan will use logical roles only.

### Assumptions and boundaries

- The current Windows workstation will be the first executor; other licensed hosts will remain unverified until separately measured.
- Any enrolled ecosystem producer will be able to use the documented contract; a claimed working origin will require an actual end-to-end test from that origin.
- Initial host capacity will be one worker, one thread, one active OrcaFlex job. Missing host limits will fail closed; CPU count will not determine licence capacity. Licence server refusal will yield a bounded failure, not a claim of available seats.
- Existing authenticated producer and per-job approval rules will remain in force. This plan will not grant standing unattended production approval.
- The rollout will use generic fixtures and private results storage. Telegram/email notifications will remain disabled for this task unless separately authorized.
- A neutral private scope will be proposed through normal Deckhand scope configuration. Its exact repository, owner, access policy, and revision will be recorded for approval before live enqueue; no client scope will be silently reused.

## Proposed execution contract

1. A producer will resolve an explicit executor alias from the canonical private inventory and call Deckhand preflight/dispatch/watch. Windows-local clients will use the same Python CLI, not a second scheduled solver task.
2. A submission will bind workflow, target, run ID, approval, source revision, complete input dependency manifest, hashes, and requested resources. The private job bundle will reject absolute/escaping paths, symlinks, unapproved workflows, and executable extensions/hooks. Initial support will cover self-contained models and included files within the bundle; external functions/scripts and outside-bundle references will fail closed.
3. The credentialed agent will stage an immutable per-run workspace, verify actual file bytes, and acquire the one host-level execution guard. The guard will be outside individual queue clones; every supported local or remote entrypoint will resolve it through the same private host configuration. It will protect managed automation only, not manually launched GUI sessions.
4. The worker will run the native smoke check in its actual task account/environment, with a bounded timeout. The readiness record will bind host role, runtime context, code revisions, Python/DLL versions, check time and expiry; legacy text PASS and stale/unbound markers will be rejected. The job itself will still acquire its licence rather than trust an earlier probe as a reservation.
5. The digitalmodel batch will validate all cases before launching, enforce worker/thread caps, isolate same-stem inputs, preserve allowed relative dependencies, and write a fresh versioned manifest before returning a nonzero verdict for any failure. Explicit mock will remain available only for offline tests and will never satisfy production acceptance.
6. Success will require process exit zero AND expected job identity AND nonempty expected case set AND mock=false AND completed=total AND failed=0 AND finite requested outputs AND required artifacts present. Result records will include input/summary/artifact digests, code/DLL versions, times, and actual resources.
7. Collection will reuse observed small-result transport without claiming atomic or complete CSV/JSON return. The open [result-return issue](https://github.com/vamseeachanta/deckhand/issues/564) will own transactional bounded returns as well as heavy-artifact leases. Heavy simulations will remain in private host storage. Automated heavy fetch will remain unavailable until authenticated ownership, expiry, path confinement and digest checks pass. The core submission release will require independently checked returned summaries and host-side simulations; missing or incomplete returned artifacts will fail acceptance.
8. Timeout/cancellation will terminate the entire owned process tree, confirm it is gone, and only then release the execution guard. If cleanup cannot be proved, the executor will become unavailable for new jobs. Crash recovery will require owner/process-identity validation, not deleting a lock based only on age.

## Implementation sequence and ownership

### A. Deployment reconciliation and native canary

The first deployment increment will qualify ordinary `solver-smoke-test` task/route operation, separately from batch onboarding and signed project canaries. It will reuse the allowlisted upstream workflow from [Deckhand 588](https://github.com/vamseeachanta/deckhand/issues/588). Its readiness measurement will not imply completion of batch/resource [550](https://github.com/vamseeachanta/deckhand/issues/550) or signed-canary [570](https://github.com/vamseeachanta/deckhand/issues/570).

Preparation will propose the existing internal `software-ops` scope with a generic fixture in an allowed repository, subject to owner confirmation of the exact repository, revision, private workdir and host mapping. It will not reuse the currently mapped client scope. The operator will preserve both active checkouts and prepare isolated producer/executor candidates. The digitalmodel smoke pin will be `a7fe3775717db3f67ff1e4d4e8733c5a9f285357`. Deckhand candidate selection will wait for reviewed integration and acceptance of [cleanup repair 591](https://github.com/vamseeachanta/deckhand/issues/591); `ea24989c521dcab30ba5428cc5c8f791d273ed36` will serve only as the discovery baseline. Preparation will consult the [cutover blockers and merged proof](../reports/2026-09-10-orcaflex-cutover-readiness.html). A PR head will not be called an integrated release.

Queue recovery will follow a separate private preview and approval under [queue owner 566](https://github.com/vamseeachanta/deckhand/issues/566). After approved writer quiescence, the operator will preserve and verify detached and original-main histories, refs, reflogs and rebase metadata before any abort or upgraded-agent startup. The heartbeat-only change scope will be rechecked after quiescence; broader changes will require replanning. Remote synchronization and process ownership will be verified before drain is declared. Failed or uncertain cleanup will retain quarantine; rollback will not reactivate a consumer before process absence and ownership are proven.

The existing smoke will require RED-first strengthening before task cutover: current probe code will not by itself prove finite values, saved-simulation reload, or enforced solver thread limits. Native acceptance will require those assertions, explicit one-thread operation and bounded owned-process cleanup. Renaming a run observation-only will not bypass this resource ceiling. Offline compatibility checks will precede activation; policy will supply explicit host aliases, solver root, smoke allowlist and a reviewed wall-clock timeout. Exact private scope mapping, effective policy and rollback backup digests will accompany the cutover request.

After the owner approves the prepared scope and cutover, the operator will rerun fresh queue/process/lock checks, switch the existing credentialed task to the pinned candidate, submit one generic request locally and then from an isolated Linux producer, and verify each request/result identity and native evidence. The Linux feature checkout will remain preserved. The ordinary smoke will not activate batch or signed-project workflows. A missing scope, failed cleanup, stale readiness or incomplete returned result will stop this increment.

The operator will inventory current tasks, agent PID, pending/running jobs, local overrides, code revisions, private aliases, and environment dependencies. Existing benchmark edits, the agent's local-only commit and all four observed untracked Linux producer files will be preserved. Before any producer update, a private path/SHA256 manifest and backup will protect those files; byte-identical originals will be verified after preparation and cutover. The operator will review the divergent agent commit and compare upstream fixes; no reset or bulk sync will touch active checkouts.

A new pinned deployment directory and dedicated environment will be prepared from reviewed revisions, initially using the upstream references recorded in evidence. Any later pin will require refreshed diff/test evidence. Host-local overrides will include the now-required host_aliases and solver_root before startup. The running agent/watchdog will not update pins automatically during rollout. An idle/drained checkpoint will precede a controlled task switch. Task export and prior environment/pin will be retained privately for rollback.

The upstream OrcaFlex smoke workflow will be reused and strengthened with finite-result assertions and saved-simulation reload. The old test-runner check will return nonzero on missing API/licence so it cannot serve as a false readiness signal. The native canary will run first under the existing working desktop context and then under the intended credentialed task context. Failure in either will block activation and retain the old working deployment.

### B. Batch correctness — digitalmodel

Dependent digitalmodel implementation will wait for independent adversarial review and owner integration of [repair PR 2081](https://github.com/vamseeachanta/digitalmodel/pull/2081). The bounded repair will retain its documented T2 review requirement: Claude and Codex plan/code reviews with material findings resolved; Gemini's recorded unavailability will remain explicit rather than imply a three-provider review. This will not reduce the broader execution plan's T3 review requirement. The authoring agent will not merge its own PR. The integrated revision will receive acceptance before it becomes a deployment pin. Green CI or a draft PR will not substitute for that gate; isolated discovery and planning will continue while it is pending.

The existing batch umbrella will link [engine base-config repair](https://github.com/vamseeachanta/digitalmodel/issues/1564) and [native YAML fidelity/failure propagation](https://github.com/vamseeachanta/digitalmodel/issues/2051), which already own the immediate blockers. It will own remaining unique case IDs, complete dependent inputs, per-model threadCount, and enforced resource configuration. Tests will precede edits. Batch result semantics will use the existing run_contract.py rather than a new exit convention. Partial failure will preserve diagnostic manifests and return failure. Fresh run directories will prevent stale files from satisfying acceptance.

### C. Dispatch and arbitration — Deckhand

Before envelope/schema implementation, discovery will compare the current source and tests for approved [dispatch 582](https://github.com/vamseeachanta/deckhand/issues/582) and [identity 581](https://github.com/vamseeachanta/deckhand/issues/581) with their approved plans and deployed state. A revision-stamped drift/reuse report will identify completed scope, remaining work and incompatible assumptions; stale approval will not authorize duplicate implementation or unreviewed expansion.

The existing batch-onboarding issue will own policy mapping and resource enforcement; it will require a revised child plan because its current scope specifies convention-only resource hints. Local submission will use the existing queue transport. [Execution trust](https://github.com/vamseeachanta/deckhand/issues/568) will retain ownership of authenticated envelopes, signing/receipts and data-plane schemas; [rejection proof](https://github.com/vamseeachanta/deckhand/issues/569) and [signed canary](https://github.com/vamseeachanta/deckhand/issues/570) will retain their separate gates. The hash-binding design below will remain a proposal for that owner's review and will not replace signed trust requirements. A generic operational smoke will not satisfy the signed-riser canary. Shared host guard and readiness changes will receive explicit child ownership before implementation.

The prototype's separate shared-pointer/task path will remain preserved until its outstanding runs have been inventoried and drained; it will then be disabled reversibly and documented as unsupported. No live task will be overwritten by an installer.

The shared queue will retain wire schema 1. A versioned execution-contract envelope inside the already-hashed workflow input will contain source revision, dependency manifest digest, resource request and unique attempt ID. Approval will bind that input digest plus target/workflow using the existing request/audit fields. The producer will validate the envelope; the new consumer will require it for OrcaFlex batch requests and compare its dependency digests against staged bytes. Repeated delivery of one attempt will be idempotent; retries will receive a new attempt ID and new approval when any bound value changes. Changes to licensed_run.py/state.py/queue.py will be limited to validation and tests needed for that binding, with no schema bump or incompatible global parser change.

Consumer-first rollout will keep the batch workflow disabled for production until every active consumer that can claim the selected target is inventoried, drained, upgraded and verified; legacy target consumers and the prototype task will remain stopped. Compatibility tests will pair old/new producers and consumers using a private fixture queue: old consumers will reject the unallowlisted batch workflow, new consumers will reject missing envelopes, and unrelated schema-1 workflows will continue to parse. No new batch request will enter the shared queue before these conditions pass. Rollback will quarantine new-contract pending requests and keep the batch workflow disabled before any legacy consumer is reactivated; it will never rely on an old consumer silently understanding new safety fields.

After validation, local task overrides will be atomically switched to the pinned adapter. All managed entrypoints will be tested for contention against the same guard. Fleet-wide licence-pool reservation will be out of scope; the first executor will stay at one worker, and adding another executor will require an explicit pool allocation decision.

### D. Measured ecosystem acceptance — workspace-hub

The operator will enumerate the live private machine registry and actual reachable producer set. Coverage will record each origin, account/context, timestamp, source revision, route, and verified/failed/untested status. Native acceptance will prove Windows-local submission plus primary-Linux submission through the same executor. Additional reachable enrolled origins will be tested with one small case, and unavailable origins will be named as unverified. Portability CI will cover Linux, Windows, and macOS without pretending it proves remote connectivity.

The runbook will show bootstrap, doctor, explicit-host submit, watch/status, small-result collect, cancellation, timeout recovery, pin upgrade, and rollback. Heavy-artifact fetch will appear as unavailable until the result-return dependency passes, then will receive its authenticated instructions. A short HTML status report will link the manifest evidence and remaining fleet gaps.

## Pseudocode

```text
submit(spec, target):
  resolve enrolled producer + authorized target
  validate workflow + scope + immutable dependency manifest
  validate requested resources against private host budget
  bind approval to input digest, revision, target and workflow
  enqueue unique request using existing Deckhand protocol

execute(request):
  verify approved request and staged bytes; reject unsafe dependencies
  acquire canonical host guard; record owner process identity
  verify fresh actual-runtime readiness; obtain licence through solver
  run bounded batch in private unique directory with one worker initially
  persist manifest; validate all required cases, finite results and hashes
  publish terminal record with real failure/success; retain diagnostics
  release guard only after owned process tree is confirmed stopped

collect(run):
  authenticate caller; verify ownership, terminal manifest and digests
  return bounded allowed summaries; reject heavy fetch until dependency passes
  after dependency approval, fetch large artifacts only explicitly
  reject paths outside leased run directory, stale leases and mismatched bytes
```

## Artifact Map / Files to Change

| Owner | Existing or proposed files | Purpose |
|---|---|---|
| workspace-hub | this plan; docs/plans/README.md; docs/reports/2026-09-09-orcaflex-execution-evidence.md; docs/reports/2026-09-09-orcaflex-fea-strategy.html | Plan, evidence, human review |
| workspace-hub | docs/solver/orcaflex-execution-runbook.html | Runbook and measured coverage |
| digitalmodel | src/digitalmodel/workflows/orcaflex_run_batch.py; src/digitalmodel/solvers/orcaflex/orcaflex_parallel_analysis.py; src/digitalmodel/run_contract.py | Batch correctness and verdict integration |
| digitalmodel | src/digitalmodel/solvers/smoke/probes.py; src/digitalmodel/solvers/smoke/workflow.py; scripts/solver_smoke_test.py | Reuse and strengthen upstream native probe |
| digitalmodel | tests/workflows/test_orcaflex_run_batch.py; tests/solvers/orcaflex/run_tests.py; proposed tests/solvers/orcaflex/test_native_execution_contract.py | RED-first regression and opt-in licensed acceptance |
| Deckhand | src/deckhand/licensed_run_agent.py; src/deckhand/licensed_run_agent_runtime.py; src/deckhand/licensed_run.py; src/deckhand/licensed_run_state.py; src/deckhand/licensed_run_queue.py; config/deckhand/policy.yml | Shared execution, strict result/readiness checks, compatible request binding and workflow onboarding |
| Deckhand | scripts/deckhand/licensed-run-ops.py; scripts/deckhand/licensed-run-agent/; docs/deckhand/licensed-run-ops.md | Portable submission and controlled deployment |
| Deckhand | tests/deckhand/test_licensed_run_agent.py; tests/deckhand/test_licensed_run_timeout.py; proposed tests/deckhand/test_orcaflex_execution_contract.py | Runtime contract tests |
| private deployment | host settings, neutral scope binding, task backup, immutable canary manifest and artifacts | Credentials/identity/data residency will remain private |

## TDD Test List

| Test | Required outcome |
|---|---|
| Missing API/licence and legacy/stale/wrong-context marker | Nonzero, no solver job success |
| Real canary statics/dynamics and simulation reload | Finite results, simulationComplete, matching file readback |
| Offline mock success sent to production collector | Rejected |
| Partial case failure or missing/empty/stale manifest | Nonzero workflow verdict and failed request |
| Same-stem files and nested includes | Unique outputs and correctly bound dependencies |
| Traversal, symlink, outside include, script hook, tampered bytes | Rejected before solver invocation |
| Resource defaults, over-budget request, thread setting | One worker/thread by default; cap enforced; no CPU-based seat inference |
| Local + remote submission contention, multiple queue clones | At most one managed process tree on the executor |
| Timeout, cancellation, process-tree kill failure, crashed owner | No premature guard release; executor quarantined on uncertain cleanup |
| Missing host_aliases, solver_root or max_wall_seconds; wrong deployment pin | Preflight fails before task switch; timeout must be finite and positive |
| Replay/retry of existing request and result | No duplicate live execution or stale-success substitution |
| Old/new producers and consumers; rollback with published requests | Wire schema 1 remains readable; unsupported contracts cannot execute; new requests quarantined before rollback |
| Small result return and heavy-fetch unavailable path | Ownership, bounds and digest checked; heavy fetch unavailable until dependency passes |
| Heavy fetch after result-return dependency | Ownership, lease, path confinement and digest checked |
| Local and Linux-origin end-to-end generic case | Same contract; actual licensed results and provenance returned |
| Rollback after failed upgrade canary | Prior task/pin restored; existing jobs and files preserved |

## Acceptance and approval boundaries

The user will approve this revision before implementation. Each existing child issue will reference the approved shared contract and retain its own lifecycle tracking; any expanded child scope will return for plan review. Code-stage review will use T3 adversarial review and legal scan. No actor will self-apply plan-approved or completeness-verified labels.

Completion will require checked-in implementation, approved deployment, successful native local and primary-Linux remote batch execution-contract runs satisfying proposed contract item 6, failure-path tests, result readback, a coverage matrix that names untested origins, and a cleanup/rollback audit. Ordinary smoke success will qualify only its task/route increment, not this full completion bar or signed-project acceptance. Arbitrary shell execution, unconstrained sweeps, automatic consumption of all licence seats, host identity migration, and customer-model validation will remain excluded.

## Risks and rollback

Session-specific licensing will be measured in the actual task account. Credential setup will use existing secure Windows mechanisms; passwords will not be printed or committed. Scope selection and private data permissions will block live enqueue until recorded. New pins may require curated dependency updates, which will occur in the new environment only. External model dependencies will be rejected until explicitly supported, not silently omitted.

Cutover will wait for both execution paths to become idle, preserve configuration/task exports, disable the prototype reversibly, and test one job. A failed canary will permit restoring backup configuration, but reactivation will require proven process-tree absence, resolved lock ownership, disabled new workflow policy, and quarantine of new-contract requests. Unresolved ownership or an unkillable process will leave both consumers disabled and queued jobs untouched; rollback will never bypass quarantine by starting the legacy agent. No cleanup will touch unrelated benchmark output or workspace sessions.
