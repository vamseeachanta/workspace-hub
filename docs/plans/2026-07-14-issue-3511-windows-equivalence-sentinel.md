# Plan for #3511: Fail-closed Windows equivalence sentinel and exact state publishing

> **Status:** plan-approved — user approved on 2026-07-14; TDD implementation authorized
> **Complexity:** T3
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3511
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** planning = parallel-readonly; implementation = isolated single-writer worktree with read-only review lanes
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3511-claude.md` | `scripts/review/results/2026-07-14-plan-3511-codex.md` | `scripts/review/results/2026-07-14-plan-3511-gemini.md` | `scripts/review/results/2026-07-14-plan-3511-independent.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/monitoring/equivalence-fingerprint.sh` currently invokes bare `python3` for identity, age calculations, and final JSON emission. It writes directly to `--out` and ends with a successful status message, so an emitter failure can leave a zero-byte file while returning zero.
- `scripts/monitoring/equivalence-sentinel.sh` currently uses `uv run --no-project python` for publishing, but it trusts the fingerprint script's return code and does not independently validate the JSON. It records `publish_rc`, continues to comparison, and returns the comparison result, so a publish failure can be masked.
- `scripts/monitoring/equivalence_state.py` currently sends string input through `subprocess.run(..., text=True)` and constructs newline-delimited `git mktree` input. Windows newline conversion can therefore alter tree-entry bytes. The publisher also hashes malformed content after `json.loads()` fails.
- `scripts/lib/python-resolver.sh` is absent. A small shared Bash resolver will be created so fingerprint generation, sentinel validation, and publish-health collection use the same verified interpreter array.
- `config/scheduled-tasks/schedule-tasks.yaml` currently declares `equivalence-sentinel` for both Windows hosts at minute 17 every six hours. PR #3512 therefore resolves roster membership; this plan will not add duplicate membership.
- `scripts/windows/setup-scheduler-tasks.ps1` currently reads YAML only for `EqualityReport`. Its cron converter supports fixed daily/weekly triggers but not `17 */6 * * *`, and the live `\Claude\` folder has no `EquivalenceSentinel` task. The folded Linux `command: >-` value is not directly renderable by its scalar reader, so this plan will add an explicit simple Windows wrapper field to the same YAML task rather than attempt lossy cron-shell translation.
- `scripts/readiness/collect-equality.sh` currently reads `publish-health.json` only through bare `python3`, so Windows can continue reporting `MISSING-EVIDENCE` even after a valid sentinel run.

### Standards and control-plane contracts

- `docs/standards/CONTROL_PLANE_CONTRACT.md` makes workspace-hub the canonical configuration and automation control plane. Windows Task Scheduler materialization will therefore consume `config/scheduled-tasks/schedule-tasks.yaml`, not introduce a second hardcoded cadence.
- `docs/plans/2026-05-30-issues-2816-2815-windows-equality-collector.md` establishes the Windows precedent: PowerShell will launch the correct Windows runtime while schedule metadata remains single-source in YAML.
- `.claude/rules/coding-style.md` requires repo-relative paths and bounded file/function size. No absolute workstation path will enter implementation code or tracked fixtures.
- Security/legal rules require fail-closed validation, no secrets, and the repository legal scan. Fingerprints will remain configuration hashes and machine metadata only; no auth material will be added.

### Related issues and changes

- [#3511](https://github.com/vamseeachanta/workspace-hub/issues/3511) is OPEN at `status:needs-plan` and owns the remaining Windows interpreter, byte-stability, sentinel, and registration defects.
- [#3516](https://github.com/vamseeachanta/workspace-hub/issues/3516) / PR [#3519](https://github.com/vamseeachanta/workspace-hub/pull/3519) supplies registry-driven identity and machine-keyed ref blobs. This plan will pin that behavior with tests rather than reimplement it.
- PR [#3512](https://github.com/vamseeachanta/workspace-hub/pull/3512) adds Windows hosts to the YAML sentinel roster, but the Windows registrar does not materialize the task.
- [#2815](https://github.com/vamseeachanta/workspace-hub/issues/2815) supplies the YAML-to-Task-Scheduler precedent but remains incomplete as a general renderer.
- [#3506](https://github.com/vamseeachanta/workspace-hub/issues/3506) remains blocked until a valid `ace-win-2.json` fingerprint lands and `publish_health` turns green.
- [#3526](https://github.com/vamseeachanta/workspace-hub/issues/3526) records the separate daily report-only full reconciliation audit. This plan will not schedule `reconcile-ecosystem.sh`, and it will never schedule unattended `--apply` behavior.

### LLM wiki and drive-file intelligence

- No LLM wiki page is applicable to this harness/infrastructure defect.
- The drive-file query `Windows equivalence scheduler sentinel` returned no relevant files. Coverage was partial: `ace_knowledge`, `dde_knowledge`, `og_standards_inventory`, `cad_readability`, and `master_document_index` each reported the exact reason `unreachable`. No drive content will be treated as implementation authority.

### Gaps identified

- No shared verified Bash interpreter resolver exists.
- No atomic, schema-validated fingerprint output contract exists.
- No pre-hash validation or byte/NUL-safe tree-plumbing contract exists.
- No sentinel exit contract preserves fingerprint/publish failure over a later comparison result.
- No Windows Task Scheduler registration exists for the already-declared sentinel cadence.
- No explicit YAML-to-Windows action contract exists for compound folded shell commands, environment binding, cron escaping, or log redirection.
- No Windows-safe publish-health reader exists in the equality collector.

### Evidence (embedded verification)

**Issue status verification — 2026-07-14:**

```text
#3511 OPEN status:needs-plan — Windows sentinel emits empty unknown fingerprint and corrupts mktree filenames
#3516 OPEN with merged implementation PR #3519 — registry identity and machine-keyed blobs
#2815 OPEN — Windows Task Scheduler single-source materialization
#3506 OPEN — ace-win-2 fingerprint absent
```

**Windows fingerprint reproduction — 2026-07-14T10:39Z:**

```text
$ bash scripts/monitoring/equivalence-fingerprint.sh --out <temporary-file>
Python was not found; run without arguments to install from the Microsoft Store ...
wrote fingerprint -> <temporary-file>
FINGERPRINT_RC=0 EXISTS=True BYTES=0
```

The runtime failure matches the issue: **YES**. The test uses a disposable temporary file and never invokes the sentinel or production ref publisher.

**Windows Git-plumbing reproduction — 2026-07-14T10:39Z:**

```text
$ uv run pytest tests/monitoring/test_equivalence_state.py tests/readiness/test_windows_scheduler_single_source.py -q
.......F..........
FAILED tests/monitoring/test_equivalence_state.py::test_same_role_machines_do_not_clobber_end_to_end
E assert [] == ['ace-win-1', 'ace-win-2']
1 failed, 17 passed
```

The real-git temporary-repository test confirms that current Windows text-mode plumbing creates a state tree that `collect()` cannot read as the two expected machines.

**Schedule and live-task proof — 2026-07-14:**

```text
YAML: equivalence-sentinel schedule="17 */6 * * *" machines include ace-win-1 and ace-win-2
Registrar: Get-EqualityReportTask is the only YAML-backed task reader
Live \Claude\ tasks: ContextManagementDaily, EqualityReport, HarnessUpdate,
MemoryBridgeSync, NightlyReadiness, RepoSync, WorkstationVersionCheck
Live EquivalenceSentinel: absent
Daily full reconcile-ecosystem task: absent (tracked separately in #3526)
```

Distinct sources consulted: issue state, current implementation, current tests, live Task Scheduler, workstation registry, prior #2815 plan, control-plane contract, and drive index.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-14-issue-3511-windows-equivalence-sentinel.md` |
| Human review plan | `docs/reports/2026-07-14-issue-3511-windows-equivalence-sentinel-plan.html` |
| Shared interpreter resolver | `scripts/lib/python-resolver.sh` |
| Fingerprint emitter | `scripts/monitoring/equivalence-fingerprint.sh` |
| Sentinel controller | `scripts/monitoring/equivalence-sentinel.sh` |
| Git-ref state store | `scripts/monitoring/equivalence_state.py` |
| Windows sentinel wrapper | `scripts/windows/equivalence-sentinel.ps1` |
| Windows scheduler renderer | `scripts/windows/setup-scheduler-tasks.ps1` |
| Equality collector | `scripts/readiness/collect-equality.sh` |
| Schedule source | `config/scheduled-tasks/schedule-tasks.yaml` |
| Shell tests | `scripts/monitoring/tests/test_equivalence_fingerprint.sh` |
| State-store tests | `tests/monitoring/test_equivalence_state.py` |
| Scheduler tests | `tests/readiness/test_windows_scheduler_single_source.py` |
| Collector tests | `tests/readiness/test_collect_equality.py` |
| Plan reviews | `scripts/review/results/2026-07-14-plan-3511-{claude,codex,gemini,independent}.md` plus preserved Codex r1/r2/unavailable history |

---

## Deliverable

The Windows equivalence sentinel will generate a validated `ace-win-2` fingerprint, publish it without filename-byte corruption, fail nonzero on any generation/publish failure, run every six hours from the canonical Windows scheduler, and expose fresh publish-health evidence to the equality matrix.

---

## Scope and Sequencing

### In scope

1. A verified interpreter resolver shared by the affected Bash paths.
2. Atomic fingerprint generation with required-field validation.
3. Strict publisher validation and exact byte/NUL-safe Git tree construction.
4. Sentinel failure propagation and publish-health recording.
5. YAML-driven Windows registration of `EquivalenceSentinel` at `:17` every six hours through an explicit PowerShell wrapper field in the canonical task entry.
6. Windows-safe equality collection of the resulting publish-health record.
7. Temporary-repository and `-WhatIf` tests that never mutate the production ref or live scheduler.
8. Post-merge operator validation on `ace-win-2`, followed by an equality report refresh and #3506 evidence comment.

### Out of scope

- Registry identity or machine-key migration already owned by #3516/#3519.
- Full Windows Task Scheduler catalog convergence beyond the sentinel; #2815 remains the broader materialization anchor.
- A daily full reconciliation audit; #3526 owns report-only design and scheduling.
- Any unattended reconciler `--apply`, `--stash-dirty`, or `--equality` mode.
- Runtime installer/link semantics owned by #3513.
- Solver-license probing owned by #2852.
- Deleting legacy ref blobs belonging to other machines; each machine will retain the self-cleaning migration contract from #3519.

---

## Pseudocode

### Fingerprint version 1 schema

The shared validator will require exactly these top-level keys; additive fields will require a version bump rather than silent acceptance:

| Field | Version-1 contract |
|---|---|
| `fingerprint_version` | integer exactly `1` (boolean rejected) |
| `role` | nonempty string in `full`, `contribute`, `contribute-minimal`, `unknown` |
| `hostname` | nonempty string without control characters |
| `machine_id` | nonempty string matching `^[A-Za-z0-9][A-Za-z0-9._-]*$` |
| `ts` | parseable RFC3339 string with explicit UTC offset |
| `clone_head` | null or 7–40 lowercase hexadecimal string |
| `behind_origin`, `ahead_origin` | null or nonnegative integer (boolean rejected) |
| `harness_version`, `harness_install` | null or nonempty string without control characters |
| `registry_sha256` | null or 64 lowercase hexadecimal characters |
| `learning_cron_ages_h` | exact two-key object; each value null or finite nonnegative number |
| `provider_soul_hashes` | exact five-key object (`hermes`, `claude`, `codex`, `codex_agents`, `gemini`), matching the current producer; each value null or 16 lowercase hexadecimal characters |
| `on_main` | boolean |
| `index_lock_stale_min` | null or finite nonnegative number |
| `last_publish_duration_s` | null or finite nonnegative number; the generator always emits this key as `null`, and sentinel preparation may replace it from a prior valid health record before final validation |

`json.loads(..., parse_constant=reject)` will reject `NaN`, `Infinity`, and `-Infinity`. Direct publisher calls and generated files will invoke the same validator. `publish(machine, content)` will add the trust-boundary check that the validated `machine_id` equals `machine`.

The publish-health file will use an independent exact schema:

| Field | Contract |
|---|---|
| `schema_version` | integer exactly `1` |
| `ts` | timezone-aware RFC3339 string |
| `phase` | `fingerprint` or `publish` |
| `duration_s` | finite nonnegative number |
| `rc` | integer in `0..4` |

Sentinel exit meanings will remain stable for comparison results (`0` info, `1` warning, `2` critical), use `3` for required fingerprint/publish/store failure, and add `4` for inability to persist the current publish-health result.

### Verified Bash interpreter resolution

```text
resolve_python():
    probe uv + "uv run --no-project python" with a zero-work command
    else probe python3 with a zero-work command
    else probe python with a zero-work command
    expose the winning command as a Bash array
    return nonzero if every candidate is absent or nonfunctional
```

### Atomic fingerprint generation

```text
generate_fingerprint(output):
    require a working interpreter array
    resolve registry identity through that same interpreter
    allow optional telemetry probes to degrade to null
    create a temporary file beside output (or in a temporary directory for stdout)
    serialize JSON into the temporary file with last_publish_duration_s=null; require emitter rc == 0
    invoke the new equivalence_state.py validate subcommand so generation and publication share one schema
    require validate to accept a fingerprint path, return zero only for the exact v1 schema,
      emit no state mutation, and return a distinct nonzero validation error otherwise
    atomically replace output, or stream validated bytes to stdout
    trap-clean temporary residue and return nonzero on any required-step failure
```

### Exact state publication

```text
publish(machine, content):
    decode content with non-standard JSON constants rejected
    validate the exact fingerprint-version-1 schema before any git write
    require integer fingerprint_version == 1
    require exact allowed top-level keys
    require nonempty string role/hostname/machine_id and safe machine key
    require role in the version-1 role enum and content.machine_id == machine
    require an RFC3339 timezone-aware timestamp
    require booleans, nullable nonnegative integers/numbers, finite ages/durations,
      and null-or-16-lower-hex provider hashes at their exact field paths
    fetch the current ref tip and parse ls-tree -z as bytes
    hash validated UTF-8 bytes
    build mktree -z input with NUL terminators and exact encoded names
    commit and push with the existing force-with-lease CAS/retry contract
    never strip carriage returns as a repair strategy
```

### Sentinel failure contract

```text
sentinel_cycle():
    run atomic fingerprint generation
    independently parse and validate the generated file, including the null duration field
    on failure: persist phase=fingerprint publish-health failure and exit before publish
    read the prior health record only when it passes the exact health schema and phase=publish;
      copy its finite nonnegative duration into a same-directory fingerprint temp,
      otherwise retain null
    validate the enriched temp before atomically replacing the generated fingerprint;
      on enrichment/write/validation failure preserve the generated valid file and exit before publish
    run publisher
    create a same-directory health temp file, serialize + validate it, flush/close it,
      then atomically replace publish-health.json
    if health create/write/validate/replace fails, preserve any prior record and exit 4
    on publish failure: exit publish failure before comparison
    only then collect and compare fleet state; return comparison severity
```

### Windows task materialization

```text
render_equivalence_sentinel():
    read the equivalence-sentinel YAML block
    resolve current machine through existing Windows identity mapping by default
    accept a validated MachineIdOverride parameter only for WhatIf/test rendering;
      reject it for live registration or removal
    skip when machine is outside the YAML roster
    convert "17 */6 * * *" to a trigger anchored at minute 17 with 6-hour repetition
    read windows_script from the same YAML task; reject missing/absolute/escaping paths
    register PowerShell with that repo-relative script and repo WorkingDirectory
    wrapper resolves canonical Git Bash, binds WORKSPACE_HUB to the repo,
      invokes equivalence-sentinel.sh, and owns Windows-native dated log redirection
    do not parse/translate the folded Linux command or its cron-specific percent escapes
    support WhatIf, replacement, removal, and idempotent re-registration
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/lib/python-resolver.sh` | One verified interpreter-array contract for Git Bash on Linux and Windows |
| Modify | `scripts/monitoring/equivalence-fingerprint.sh` | Remove bare `python3`; add atomic validated output and required-step failure semantics |
| Modify | `scripts/monitoring/equivalence-sentinel.sh` | Validate before publish and preserve fingerprint/publish failure status |
| Modify | `scripts/monitoring/equivalence_state.py` | Add a side-effect-free `validate` CLI subcommand, reject invalid payloads, and use byte/NUL-safe tree plumbing |
| Create | `scripts/windows/equivalence-sentinel.ps1` | Resolve Git Bash, bind the repo environment, run the sentinel, and write Windows-native logs without translating cron shell syntax |
| Modify | `scripts/windows/setup-scheduler-tasks.ps1` | Read the YAML `windows_script`, render/register it, support the exact `*/6` cadence, and expose a WhatIf-only machine override test seam |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Add a repo-relative `windows_script` to the existing entry and reconcile the false `python3` capability requirement; do not change roster/cadence |
| Modify | `scripts/readiness/collect-equality.sh` | Read publish-health through the verified resolver on Windows |
| Modify | `scripts/readiness/build-equality-matrix.py` | Fail closed unless collected publish health has a valid aware timestamp, integer rc, and finite nonnegative duration before freshness grading |
| Modify | `scripts/monitoring/tests/test_equivalence_fingerprint.sh` | Add interpreter-stub, atomicity, schema, and identity tests without relying on system `python3` |
| Modify | `tests/monitoring/test_equivalence_state.py` | Add validate-subcommand CLI, invalid-input, no-mutation, and exact-name Windows regression coverage |
| Modify | `tests/readiness/test_windows_scheduler_single_source.py` | Pin YAML-driven sentinel action, cadence, roster, WhatIf, and removal behavior |
| Modify | `tests/readiness/test_collect_equality.py` | Pin Windows publish-health collection through the resolver |
| Modify | `tests/readiness/test_publish_health_verdict.py` | Extend fail-closed matrix coverage for syntactically invalid/naive timestamps and missing or wrong-type rc/duration facts |
| Update | `scripts/windows/README.md` | Document registration, safe manual validation, and rollback commands |
| Update | `docs/plans/README.md` | Index this reviewed plan |

No implementation file will be modified until the reviewed plan receives explicit user approval.

---

## TDD Test List

| Test | Verification | Expected result |
|---|---|---|
| `test_resolver_ignores_store_python3_stub` | `python3` is discoverable but cannot execute; working `uv`/`python` remains available | working interpreter array selected |
| `test_resolver_fails_when_all_candidates_broken` | every candidate returns nonzero | resolver and fingerprint return nonzero |
| `test_fingerprint_success_is_nonempty_valid_json` | nominal generation | required fields parse and match registry identity |
| `test_fingerprint_failure_preserves_previous_valid_output` | emitter fails after a prior good file | prior file remains byte-identical |
| `test_ace_win_2_identity_regression` | registry alias resolution | `ace-win-2`, `contribute-minimal` |
| `test_schema_rejects_wrong_types_version_and_key_set` | null/bool/string identity/version values plus missing/extra keys | validation error before Git write |
| `test_schema_rejects_bad_timestamp_and_nonfinite_numbers` | naive/invalid timestamp and NaN/Infinity/negative numeric fields | validation error before Git write |
| `test_schema_accepts_nullable_optional_telemetry` | documented null telemetry with otherwise exact v1 payload | validation succeeds |
| `test_generator_and_sentinel_duration_preparation_order` | generator emits `last_publish_duration_s=null`; only valid `phase=publish` prior health supplies a finite duration; fingerprint-phase/invalid/missing health does not; injected enriched-temp validation failure | generated and final payloads each pass the same exact schema; temp is validated before atomic replacement; a failed enrichment preserves the generated valid file and blocks publish |
| `test_validate_cli_is_side_effect_free` | invoke `equivalence_state.py validate <fingerprint>` against valid and invalid fixtures while Git commands are trapped | valid returns zero; invalid returns nonzero; neither path invokes Git or mutates files |
| `test_publish_rejects_empty_json_before_git_write` | empty payload | validation error; no hash/commit/push invocation |
| `test_publish_rejects_malformed_or_nonobject_json` | malformed/list payload | validation error; ref unchanged |
| `test_publish_rejects_machine_mismatch_and_unsafe_key` | mismatched field or control/path characters | validation error; ref unchanged |
| `test_mktree_exact_names_under_windows_crlf` | temporary real Git repository on Windows | exact names, no CR suffix |
| `test_same_role_machines_do_not_clobber_end_to_end` | existing real-Git regression | both Windows machines collect successfully |
| `test_publish_preserves_unrelated_entries_and_retries_cas` | concurrent tip movement | all unrelated entries survive; bounded retry succeeds/fails honestly |
| `test_invalid_fingerprint_blocks_publish` | zero-byte/missing required field | publisher is not invoked; health rc nonzero |
| `test_publish_failure_cannot_be_masked_by_green_compare` | publisher nonzero, comparator zero | cycle exits nonzero |
| `test_publish_health_write_is_atomic` | interrupted write simulation | prior valid health record or complete new record, never partial JSON |
| `test_publish_health_persistence_failure_exits_four` | temp-create/write/validate/replace failure injection | cycle exits 4 even when compare would return zero |
| `test_windows_whatif_renders_equivalence_sentinel_for_each_rostered_host` | `-WhatIf -MachineIdOverride` separately for `ace-win-1` and `ace-win-2` | `\Claude\EquivalenceSentinel` appears for each host with the same YAML action/cadence |
| `test_windows_machine_override_is_whatif_only` | pass `MachineIdOverride` without `-WhatIf`, including removal mode | fail closed before scheduler mutation |
| `test_windows_sentinel_trigger_is_minute_17_every_six_hours` | YAML `17 */6 * * *` | exact repetition interval and anchor |
| `test_windows_sentinel_action_comes_from_yaml` | compare rendered PowerShell script/cadence to task fields | no separately hardcoded action or schedule |
| `test_windows_wrapper_binds_repo_and_translates_no_cron_syntax` | temp repo path containing spaces; stub Git Bash | exact script invocation, WORKSPACE_HUB binding, native log path, no `\%`/`$(date)` leakage |
| `test_windows_renderer_rejects_unsafe_wrapper_path` | absolute/traversal/missing `windows_script` | fail closed before registration |
| `test_windows_sentinel_machine_roster_and_remove` | included/excluded host plus `-Remove` | correct install/skip/removal behavior |
| `test_windows_publish_health_uses_working_interpreter` | Store stub plus working fallback | equality output contains fresh timestamp/duration/rc |
| expanded `tests/readiness/test_publish_health_verdict.py` freshness/schema cases | absent/sentinel, invalid-syntax, timezone-naive, future, and older-than-26-hour timestamps plus missing/wrong-type rc and duration, explicitly including booleans | matrix remains fail-closed (`MISSING-EVIDENCE` or `PUBLISH-STALE`), never green |
| existing equivalence, scheduler, schedule-validator, and matrix suites | regression | all pass |

Tests that require invalid JSON or corrupt-name fixtures will use temporary directories and isolated bare repositories. No fixture will touch the production `equivalence-state` ref, and no blanket enforcement exemption will be added.

---

## Acceptance Criteria

- [ ] RED is captured first for the Store-stub zero-byte fingerprint and Windows real-Git tree failure.
- [ ] All required fingerprint stages fail closed while optional telemetry continues to emit `null` where documented.
- [ ] A failed generation never truncates or replaces the last valid fingerprint.
- [ ] Empty, malformed, non-object, wrong-type/version/timestamp, non-finite, mismatched-machine, unsafe-key, missing-key, and extra-key payloads are rejected before Git object/ref mutation.
- [ ] Real Git integration tests prove exact filenames and successful collection on Windows and Linux.
- [ ] Sentinel publish failure cannot be overwritten by comparator success.
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` remains the only cadence/action source for the Windows sentinel; its repo-relative `windows_script` resolves through a tested wrapper without parsing the folded Linux command.
- [ ] `setup-scheduler-tasks.ps1 -WhatIf -MachineIdOverride <host>` deterministically renders `\Claude\EquivalenceSentinel` at minute 17 every six hours for each of `ace-win-1` and `ace-win-2`; the override is rejected for any live mutation.
- [ ] Any publish-health persistence failure returns exit 4 and cannot be masked by comparison success or a stale prior health record.
- [ ] Expanded matrix freshness/schema tests prove absent/sentinel, invalid-syntax, timezone-naive, future, and older-than-26-hour timestamps plus missing/wrong-type/boolean rc and duration facts cannot render `PUBLISH-OK`.
- [ ] Focused tests pass, plus `uv run --no-project python scripts/cron/validate-schedule.py` and affected monitoring/readiness suites.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes on the implementation diff.
- [ ] Code/artifact adversarial review completes at T3 depth; unavailable providers are recorded rather than treated as approvals.
- [ ] Post-merge operator validation runs from a clean/current canonical `ace-win-2` checkout and proves: nonempty fingerprint, `machine_id=ace-win-2`, exact ref entry `ace-win-2.json`, no CR-suffixed names, task last result zero, and fresh publish-health rc zero.
- [ ] The equality report is refreshed only after the valid fingerprint lands; the live matrix publish-health cell becomes green.
- [ ] An implementation summary with test/live evidence is posted to #3511 and operational completion evidence is posted to #3506.
- [ ] #3506 closes only after its live done condition is verified; #3511 follows the completeness gate before close.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | initial and focused reruns timed out without a usable review |
| Codex | MINOR (r3) | no blockers; requested explicit provider-key enumeration and explicit retention of stale/missing publish-health matrix tests |
| Gemini | UNAVAILABLE | no non-interactive Gemini authentication configured |
| Independent read-only lane | MINOR (r2) | r1 blockers resolved; r2 precision fixes restrict enrichment to publish-phase health and validate temp content before atomic replacement |

**Overall result:** PASS with provider degradation — Codex r3 and independent r2 report no blockers. Claude timed out and Gemini lacks non-interactive authentication; both remain `UNAVAILABLE`, not approvals. All MAJOR findings and final MINOR precision findings are incorporated.

Revisions made after Codex r1:

- Replaced underspecified folded-command translation with an explicit YAML `windows_script` plus a Windows-native wrapper contract and escaping tests.
- Defined a strict fingerprint-version-1 schema, shared validator, and wrong-type/version/timestamp/non-finite test matrix.
- Made publish-health persistence a required atomic stage with dedicated exit 4 and injected failure coverage.
- Replaced the bare schedule-validator command with the canonical `uv run --no-project python` form.
- Specified a side-effect-free `equivalence_state.py validate` subcommand and direct CLI/no-mutation tests.
- Added a `WhatIf`-only `MachineIdOverride` seam so both rostered Windows hosts can be rendered and verified deterministically without scheduler mutation.
- Corrected the exact provider hash set to include the producer's `codex_agents` key.
- Made the generator emit a null duration, then required sentinel enrichment plus atomic final revalidation before publish.
- Expanded fail-closed publish-health tests for invalid/naive timestamps and missing or wrong-type rc/duration facts.
- Restricted duration enrichment to prior publish-phase health and required enriched-temp validation before atomic replacement; boolean health facts are explicit invalid-type cases.

---

## Risks and Open Questions

- **Remote-ref corruption:** Any text-mode or partial-input path can damage shared fleet evidence. Mitigation: validation before Git writes, byte/NUL plumbing, isolated tests, and live rollout only after reviewed code lands.
- **False fallback success:** `command -v` alone accepts the Windows Store stub. Mitigation: every resolver candidate must execute a probe successfully.
- **Over-broad `set -e`:** Optional metrics intentionally degrade to `null`. The implementation will check required identity/serialization/publish operations explicitly instead of making every best-effort probe fatal.
- **Schedule duplication:** Hardcoding a PowerShell action or cadence would create a second authority. The renderer will consume the YAML block and tests will compare the rendered contract to that source.
- **Cross-shell quoting:** The Linux folded command contains `$WORKSPACE_HUB`, `$(date)`, redirection, and cron percent escapes. Windows will not translate that string. The canonical task will name a repo-relative PowerShell wrapper that owns native environment/log semantics and invokes only the canonical sentinel script through resolved Git Bash.
- **Trigger approximation:** A once-daily trigger is not equivalent to `17 */6 * * *`. Tests will inspect the six-hour repetition interval and minute anchor.
- **Live scheduler mutation:** Registration changes affect the host. Tests and review use `-WhatIf`; actual registration and one-shot validation occur only after merge from the canonical checkout.
- **Checkout churn:** Current ace-win-2 main is dirty and behind because scheduled outputs recur. Live validation will stop if the checkout is not current/clean; it will not pop the preserved stash or discard unrelated state.
- **Broader scheduler drift:** Multiple YAML-eligible Windows tasks are absent or differently materialized. This plan will not claim general scheduler parity; #2815 remains the broader anchor, and #3526 owns daily report-only reconciliation.
- **No drive precedent:** Drive search returned no relevant files with multiple indexes unreachable. Repository code/tests and live Windows evidence remain the authoritative inputs.

---

## Complexity: T3

This change crosses Bash, Python Git plumbing, PowerShell Task Scheduler semantics, shared remote state, Windows/Linux behavior, and live fleet evidence. It requires three-provider plan/code review depth where available and an operator-gated Windows rollout.
