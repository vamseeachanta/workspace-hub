# Plan for #2269: standardize OpenFOAM v2312 baseline workflow and validation

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-04-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2269
> **Review artifacts:** scripts/review/results/2026-04-15-plan-2269-claude.md | scripts/review/results/2026-04-15-plan-2269-codex.md | scripts/review/results/2026-04-15-plan-2269-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/openfoam/run-openfoam-tutorials.sh` — current CLI contract is `bash scripts/openfoam/run-openfoam-tutorials.sh [--verdict /path/to/verdict.yaml]`; it sources `/usr/lib/openfoam/openfoam2312/etc/bashrc`, runs `cavity` and `damBreak`, writes YAML with `generated_at`, `machine`, `openfoam_version`, `overall_verdict`, and per-tutorial status/time-directory counts, and exits non-zero on failure. This is the strongest existing execution engine to reuse underneath a new operator-facing validator.
- Found: `docs/research/openfoam-tutorials.md` — repo research records that OpenFOAM ESI v2312 is installed on dev-secondary, that `pitzDaily` converged in 281 iterations, and that `cavity`/`damBreak` were later completed headlessly; this provides both a fast smoke-case candidate (`cavity`) and a stronger benchmark candidate (`pitzDaily`) with known expected behavior.
- Found: `docs/research/openfoam-version-landscape.md` — explicitly recommends the ESI/OpenFOAM.com fork with v2312 syntax for dev-secondary and documents fork-specific dict differences (`turbulenceProperties`, `transportProperties`, `scale`) that the baseline doc must freeze.
- Found: `scripts/pipelines/stubs/stub_openfoam.py` — repo already has a synthetic OpenFOAM stub for higher-level pipeline validation, confirming there is currently no canonical operator-facing baseline workflow doc for real solver execution.
- Found: `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` — the baseline workflow package should satisfy the existing reusable-artifact bundle expectations for engineering delivery instead of inventing a parallel contract.
- Gap: no canonical plan artifact existed yet for #2269 under `docs/plans/` before this draft.
- Gap: no repo-tracked OpenFOAM baseline runbook exists under `docs/engineering/portability/`, and no reproducible smoke-case manifest/example path currently exists in the repo.

### Standards
| Standard | Status | Source |
|---|---|---|
| OpenFOAM portability baseline (ESI v2312 on dev-secondary) | done / normative baseline exists | `docs/engineering/portability/PORTABILITY_CONTRACT.md` |
| Engineering artifact portability / machine-role policy | done | `docs/engineering/portability/MACHINE_ROLES.md`, `config/workstations/registry.yaml` |
| External design-code implementation | not applicable for this issue | issue #2269 scope is tool/workflow standardization, not a DNV/API calculation implementation |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` — existing engineering wiki page confirms the capability model: case setup, solver execution, failure diagnosis, validation against tutorial benchmarks, and VTK/ParaView post-processing.

### Documents consulted
- GitHub issue #2269 — defines the portability baseline goal, required deliverables, and acceptance criteria for standardizing the OpenFOAM workflow.
- GitHub issue #25 — historical OpenFOAM capability issue showing the broader digitalmodel/OpenFOAM capability exists, but documentation remained deferred; #2269 is the bounded portability/documentation/validation follow-on.
- `docs/engineering/portability/PORTABILITY_CONTRACT.md` — locks OpenFOAM (ESI) v2312 on dev-secondary as the canonical CFD baseline and defines which artifacts must become repo-tracked portable knowledge.
- `config/workstations/registry.yaml` — confirms dev-secondary (`ace-linux-2`) is the engineering execution machine with `openfoam`, `paraview`, `gmsh`, and `tmux` installed.
- `data/document-index/online-resource-registry.yaml` — contains both the upstream OpenFOAM core repo entry and the ESI/OpenCFD fork entry, reinforcing that the plan should document which fork/baseline this repo standardizes.
- `docs/document-intelligence/data-intelligence-map.md` and `docs/document-intelligence/README.md` — confirm where engineering registries and intelligence entry points live for future discoverability, so the baseline plan can anchor its sources to the canonical intelligence surfaces.

### Gaps identified
- Gap: no canonical local plan exists for #2269.
- Gap: no repo-tracked baseline workflow doc currently states the exact OpenFOAM fork/version, environment bootstrap, runner commands, evidence artifacts, and failure modes for the workspace-hub engineering host.
- Gap: no canonical reproducible smoke-case manifest/example path currently exists in the repo for OpenFOAM baseline validation.
- Gap: the current sources disagree on bootstrap path (`/usr/lib/openfoam/openfoam2312/etc/bashrc` in the runner vs `/opt/openfoam2312/etc/bashrc` in research notes), so implementation must normalize the incorrect source after live verification rather than leaving both as active truths.
- Gap: existing `run-openfoam-tutorials.sh` is useful but not yet framed as the canonical operator-facing baseline validator with explicit prerequisites, output path contract, and failure-mode guidance.

<!-- Verification: distinct sources >= 3. Current count: 9 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` |
| Planning index row | `docs/plans/README.md` |
| Canonical baseline workflow doc | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` |
| Baseline validator wrapper | `scripts/openfoam/verify-openfoam-baseline.sh` |
| Existing tutorial runner / execution engine | `scripts/openfoam/run-openfoam-tutorials.sh` |
| Smoke-case manifest/example | `examples/openfoam/cavity-v2312/README.md` |
| Engineering delivery contract | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2269-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2269-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2269-gemini.md` |

---

## Deliverable

A repo-tracked OpenFOAM baseline package for dev-secondary that freezes ESI/OpenFOAM.com v2312 as the canonical fork/version, documents the exact workflow and failure modes, provides a repo-tracked smoke manifest for a mandatory `cavity` smoke run plus an optional `pitzDaily` benchmark, and exposes a deterministic validator wrapper that emits explicit pass/fail YAML evidence to a standardized default path with optional caller override.

---

## Pseudocode

```text
inspect existing OpenFOAM research notes, issue #2269 acceptance criteria, the existing tutorial runner, and the portability/delivery contracts
lock the canonical baseline:
    machine = dev-secondary
    fork = ESI / OpenFOAM.com
    version = v2312
    mandatory smoke case = cavity
    optional benchmark case = pitzDaily
    default verdict path = logs/engineering/openfoam-baseline/latest-verdict.yaml
probe bootstrap paths in fixed order using:
    OPENFOAM_BASHRC_PATHS if set (test-only dependency-injection override; not for normal operator use)
    otherwise the permanent supported baseline list:
        1. /usr/lib/openfoam/openfoam2312/etc/bashrc
        2. /opt/openfoam2312/etc/bashrc
    record every attempted path in stderr/log context
    if both baseline paths exist:
        first path in probe order wins
        log that the secondary path was skipped
    source the selected path
    inspect `$WM_PROJECT_VERSION`, `foamVersion`, and `$WM_PROJECT_DIR`
    parse rule:
        WM_PROJECT_VERSION must equal `v2312`
        foamVersion stdout must contain `2312`
        WM_PROJECT_DIR basename must resolve to `openfoam2312`
    verification_method field must be exactly:
        `WM_PROJECT_VERSION=v2312; foamVersion~2312; WM_PROJECT_DIR=<resolved_path>`
    if any check fails: exit non-zero with explicit version-mismatch error
    if neither path exists: fail with explicit missing-bashrc error and no silent fallback
responsibility split:
    run-openfoam-tutorials.sh remains the execution engine for tutorial runs, raw tutorial verdict generation, and tutorial selection filtering
    verify-openfoam-baseline.sh becomes the only operator-facing entrypoint; it resolves bootstrap path, verifies fork/version via `$WM_PROJECT_VERSION`, `foamVersion`, and `$WM_PROJECT_DIR`, chooses output path, invokes the runner, and emits the final normalized YAML artifact
YAML artifact contract:
    default path = logs/engineering/openfoam-baseline/latest-verdict.yaml
    wrapper must create the parent directory if missing
    the logs/ artifact is operational output, not a git-tracked deliverable
    optional override flag `--verdict` redirects output and must be forwarded to the delegated runner output path contract
    required top-level fields = generated_at, machine, resolved_bashrc_path, fork, version, verification_method, overall_verdict, tutorials
    required `tutorials` structure = list of objects, for example:
        tutorials:
          - name: cavity
            status: PASS
            time_directories: 501
    required per-tutorial fields =
        name: string
        status: enum PASS|FAIL|NOT_FOUND
        time_directories: integer >= 0
    overall_verdict: enum PASS|FAIL
    failure artifact policy:
        wrapper still writes a verdict file on failure to the same target path
        minimum failure schema = generated_at, machine, resolved_bashrc_path (if known), verification_method (if reached), overall_verdict=FAIL, tutorials (possibly empty), error_summary
    generated_at is the only allowed volatile field; all others must be deterministic for a fixed environment/result
    wrapper owns final artifact schema even if it imports tutorial rows from the runner
YAML handoff strategy:
    wrapper invokes runner with a temporary verdict path and an explicit tutorial-selection contract
    wrapper uses embedded Python via `python3` (not bash-native YAML editing) to load runner YAML, validate tutorial rows, add wrapper-owned fields, and write the final normalized artifact
write a baseline workflow doc that records:
    supported fork/version
    bootstrap path contract and probe order
    mandatory smoke case plus optional benchmark case
    exact YAML verdict schema and default artifact location
    failure modes and troubleshooting guidance
create a repo-tracked smoke manifest/example path for cavity-v2312 that documents exact reproducible commands and required headings:
    headings = Overview, Prerequisites, Commands, Expected Outputs, Failure Modes
    copy from the system tutorial into a temp/run directory
    run blockMesh then icoFoam
    point operators to the canonical validator for routine checks
    do not commit copied tutorial case data
verify behavior:
    validator succeeds in supported env and produces schema-valid YAML verdict
    validator fails with explicit message when bootstrap path is missing
    validator surfaces delegated runner failure without masking root cause
    validator records exact verification_method content
    fixture-only tests run on any host; openfoam-marked tests run only where OpenFOAM is installed
    optional benchmark runs only when wrapper is invoked with `--benchmark pitzDaily`
    invalid benchmark values fail fast with explicit unsupported-benchmark error
    damBreak remains runner-internal coverage and must be filtered out of canonical baseline output unless explicitly promoted later
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/plans/README.md` | keep local plan index/state aligned with actual review state |
| Create | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` | canonical operator-facing baseline workflow doc with traceable requirements coverage |
| Create | `scripts/openfoam/verify-openfoam-baseline.sh` | operator-facing wrapper that resolves bootstrap path, verifies version, and emits normalized YAML verdicts |
| Update | `scripts/openfoam/run-openfoam-tutorials.sh` | tighten its CLI/verdict schema contract and add explicit tutorial-selection support so wrapper can exclude non-canonical baseline tutorials |
| Update | `docs/research/openfoam-tutorials.md` | normalize any stale bootstrap-path claim after live verification so research docs stop disagreeing with the canonical validator contract |
| Create | `examples/openfoam/cavity-v2312/README.md` | repo-tracked smoke-case manifest/example path with required structural sections and exact copy/run commands |
| Create | `tests/openfoam/test_verify_openfoam_baseline.py` | behavioral pytest harness split into fixture-only schema tests and host-required `@pytest.mark.openfoam` tests |
| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | add explicit cross-reference from the OpenFOAM baseline package; required, not conditional |
| Update | `docs/README.md` | add discoverability link to the canonical OpenFOAM baseline workflow; required, not conditional |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_verify_script_succeeds_and_emits_schema_valid_verdict` | validator succeeds in a supported environment and writes schema-valid YAML to the default path or explicit override path | supported dev-secondary environment | exit 0 + YAML containing required typed fields and normalized tutorial rows |
| `test_verify_script_fails_when_bashrc_missing` | validator fails fast with explicit missing-bashrc error when neither supported bootstrap path exists | test override `OPENFOAM_BASHRC_PATHS` points to nonexistent fixtures | non-zero exit + exact missing-bashrc message naming probe order |
| `test_verify_script_surfaces_runner_failure` | validator does not mask delegated tutorial-runner failures | runner returns non-zero via fixture/stubbed temp verdict path or `OPENFOAM_TUTORIAL_RUNNER_PATH` override | non-zero exit + preserved runner failure reason in stderr/log/verdict |
| `test_verify_script_records_fork_version_via_named_mechanism` | validator proves reported fork/version using `$WM_PROJECT_VERSION`, `foamVersion`, and `$WM_PROJECT_DIR` | supported environment or mocked version command output | verdict records exact `verification_method` string format |
| `test_verify_script_normalizes_final_yaml_contract` | wrapper emits the final normalized YAML schema even when reusing runner-produced tutorial rows | successful wrapped runner output fixture | top-level schema matches canonical contract, tutorial rows match typed constraints, and only `generated_at` is volatile |
| `test_verify_script_prefers_first_supported_bashrc_path` | dual-path installations follow the permanent two-path baseline policy deterministically | two fixture bashrc paths exist in probe order | first path wins and secondary path is logged as skipped |
| `test_verify_script_rejects_invalid_benchmark_value` | wrapper fails fast when benchmark input falls outside issue scope | `--benchmark badcase` | non-zero exit + explicit unsupported-benchmark error naming allowed values |
| `test_manifest_instructions_do_not_commit_case_data` | smoke manifest is documentation/instructions only, not a committed tutorial case copy | repo tree | `examples/openfoam/cavity-v2312/README.md` present, contains required headings, and no copied OpenFOAM case tree under the example path |
| `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc cross-references issue #2269 requirements, default artifact path, smoke/benchmark tiers, troubleshooting contract, benchmark trigger, and `damBreak` status | workflow doc text | explicit requirement-to-deliverable mapping table/checklist |
| `test_pytest_harness_covers_validator_contract` | the repo contains an explicit pytest harness for validator behavior and schema checks | repo tree | `tests/openfoam/test_verify_openfoam_baseline.py` exists with validator-oriented cases, `@pytest.mark.openfoam` host-required tests, and fixture-only schema tests runnable anywhere |

---

## Acceptance Criteria

- [ ] `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` explicitly declares the canonical fork/version, permanent two-path bootstrap baseline, both-paths-exist policy, mandatory `cavity` smoke tier, optional `pitzDaily` benchmark tier, benchmark trigger mechanism, `damBreak` runner-only status, default verdict path, and troubleshooting guidance.
- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` succeeds in a supported environment and emits schema-valid YAML evidence containing exact required fields: `generated_at`, `machine`, `resolved_bashrc_path`, `fork`, `version`, exact `verification_method`, `overall_verdict`, and typed tutorial result rows; only `generated_at` may remain volatile.
- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` fails with explicit, testable messaging when neither supported bootstrap path exists, writes a failure verdict artifact with the minimum failure schema, records the attempted probe order, and surfaces delegated runner failures without masking the root cause.
- [ ] `examples/openfoam/cavity-v2312/README.md` exists as a manifest/instructions surface only; it does not commit copied tutorial case data into git, contains the required headings, and explicitly documents the reproducible tutorial-copy commands.
- [ ] `tests/openfoam/test_verify_openfoam_baseline.py` exists and serves as the explicit pytest harness for validator success/failure/schema behavior, with `@pytest.mark.openfoam` for host-dependent tests, fixture-only schema tests runnable anywhere, a dual-path probe test, and an invalid-benchmark-value test.
- [ ] The implementation explicitly documents and preserves the responsibility split between `verify-openfoam-baseline.sh` (wrapper/final YAML owner using `python3` embedded normalization) and `run-openfoam-tutorials.sh` (execution engine/raw tutorial results plus tutorial filtering).
- [ ] Any stale bootstrap-path claim in `docs/research/openfoam-tutorials.md` or the runner is normalized so repo sources no longer disagree about the supported path contract.
- [ ] The new baseline workflow is linked from `docs/README.md`.
- [ ] The workflow doc contains explicit traceability from issue #2269 requirements to deliverables/tests/acceptance criteria.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | bootstrap-path both-exist policy, YAML handoff choice, pytest host strategy, and `damBreak` status needed tightening |
| Codex | MAJOR | runtime-truth decision must be more explicitly retrieval-backed; failure-artifact policy and deterministic fixture language still needed |
| Gemini | MAJOR | dependency-injection/testability, YAML normalization mechanics, and benchmark/runner handoff needed sharper exactness |

**Overall result:** FAIL — still not approval-ready. Wave 3 narrowed the remaining blockers further, but unresolved MAJOR findings still remain around retrieval-backed runtime truth, failure-artifact policy, exact test seams, and the final approval-ready structure of workflow-doc and manifest checks.

Revisions made based on wave-3 review:
- converted bootstrap probing into a permanent two-path baseline with explicit precedence and test-only override seam
- strengthened version verification to use `$WM_PROJECT_VERSION`, `foamVersion`, and `$WM_PROJECT_DIR`
- pinned exact `verification_method` string format
- expanded failure-artifact policy and YAML schema example
- pinned embedded `python3` normalization, tutorial-selection support, invalid-benchmark behavior, and `damBreak` runner-only scope
- made README/checklist updates explicitly required and added required manifest headings

---

## Requirement traceability

| Issue #2269 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
|---|---|---|---|
| declare target fork/version explicitly | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_verify_script_records_fork_version_via_named_mechanism` | baseline workflow doc declares fork/version; validator records verification mechanism |
| canonical runner command(s) documented | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `examples/openfoam/cavity-v2312/README.md` | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc + manifest provide operator-facing commands |
| minimal smoke case under reproducible repo-tracked path | `examples/openfoam/cavity-v2312/README.md` | `test_manifest_instructions_do_not_commit_case_data` | manifest exists as instruction-only reproducible path with explicit copy/run commands |
| validator produces pass/fail output with explicit checks | `scripts/openfoam/verify-openfoam-baseline.sh`, `tests/openfoam/test_verify_openfoam_baseline.py` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_surfaces_runner_failure`, `test_verify_script_normalizes_final_yaml_contract` | validator emits schema-valid pass/fail YAML and preserves root-cause failure behavior |
| common failure modes and version/fork mismatches documented | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `docs/research/openfoam-tutorials.md` | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc contains troubleshooting + stale path claims normalized |
| workflow executable on canonical engineering host with documented prerequisites | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_fails_when_bashrc_missing` | success and failure behavior both pinned for dev-secondary |
| validator/common benchmark path clarity | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_workflow_doc_covers_traceable_issue_requirements` | wrapper documents how optional `pitzDaily` benchmark is invoked and clarifies `damBreak` is runner-internal/non-canonical baseline scope unless explicitly promoted |

---

## Risks

- **Risk:** issue #25 claims broad capability completion in digitalmodel while #2269 is a narrower portability/documentation slice; the implementation must avoid reopening the larger capability scope.
- **Risk:** current repo sources disagree on bootstrap path; implementation must normalize stale references while preserving the permanent supported two-path baseline contract.
- **Risk:** the current runner executes `damBreak` in addition to `cavity`; the baseline workflow must keep `damBreak` explicitly outside the canonical acceptance contract unless promoted in a later change.

## Decisions

- **Decision:** permanent supported bootstrap baseline = `/usr/lib/openfoam/openfoam2312/etc/bashrc` first, `/opt/openfoam2312/etc/bashrc` second.
- **Decision:** if both supported paths exist, the first in probe order wins and the second is logged as skipped.
- **Decision:** mandatory fast smoke tier = `cavity`.
- **Decision:** optional deeper benchmark tier = `pitzDaily`, invoked only via explicit wrapper flag `--benchmark pitzDaily`.
- **Decision:** invalid benchmark values fail fast with an unsupported-benchmark error naming allowed values.
- **Decision:** `damBreak` may remain in the delegated runner for broader execution coverage, but it is not part of the canonical baseline acceptance contract for #2269.
- **Decision:** default verdict path = `logs/engineering/openfoam-baseline/latest-verdict.yaml`, with optional caller override via CLI flag `--verdict` for ad hoc runs.
- **Decision:** example manifest remains instruction-only and must not commit copied tutorial case data into git.
- **Decision:** discoverability target is `docs/README.md` explicitly.
- **Decision:** host-required validator tests use `@pytest.mark.openfoam`; fixture-only schema/normalization tests run on any host.

---

## Complexity: T2

**T2** — bounded documentation + validation standardization across a small set of repo files, with one existing script to refine and one new deterministic wrapper/example path to add.
