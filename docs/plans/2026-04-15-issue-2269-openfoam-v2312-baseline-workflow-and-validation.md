# Plan for #2269: standardize OpenFOAM v2312 baseline workflow and validation

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-15 (v2 revised 2026-04-21)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2269
> **Review artifacts (v1):** scripts/review/results/2026-04-15-plan-2269-claude.md | scripts/review/results/2026-04-15-plan-2269-codex.md | scripts/review/results/2026-04-15-plan-2269-gemini.md
> **Review artifacts (v1 refreshed 2026-04-21):** scripts/review/results/2026-04-21-plan-2269-codex.md | scripts/review/results/2026-04-21-plan-2269-gemini.md
> **Review artifacts (v2 self-review):** scripts/review/results/2026-04-21-plan-2269-claude-rev-2.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/openfoam/run-openfoam-tutorials.sh` — current runner CLI contract is `bash scripts/openfoam/run-openfoam-tutorials.sh [--verdict /path/to/verdict.yaml] [--tutorials cavity[,pitzDaily]]`; it currently sources `${OPENFOAM_BASHRC:-/usr/lib/openfoam/openfoam2312/etc/bashrc}` itself (confirmed at `run-openfoam-tutorials.sh:10,31-33`), runs `cavity` and `damBreak` by default, writes YAML with `generated_at`, `machine`, `openfoam_version`, `overall_verdict`, and per-tutorial status/time-directory counts, and exits non-zero on failure. This plan retires that self-bootstrap behavior — see §Wrapper/Runner Contract below.
- Found: `scripts/openfoam/verify-openfoam-baseline.sh` — a v1-landed wrapper scaffold already exists on disk from the prior approval cycle (confirmed 2026-04-21). It currently embeds Python via `python3` fallback; this plan re-scopes it to `uv run python` on Linux. Plan implementation must edit in place, not re-create.
- Found: `docs/research/openfoam-tutorials.md` — repo research records that OpenFOAM ESI v2312 is installed on dev-secondary, that `pitzDaily` converged in 281 iterations, and that `cavity`/`damBreak` were later completed headlessly; this provides both a fast smoke-case candidate (`cavity`) and a stronger benchmark candidate (`pitzDaily`).
- Found: `docs/research/openfoam-version-landscape.md` — explicitly recommends the ESI/OpenFOAM.com fork with v2312 syntax for dev-secondary and documents fork-specific dict differences (`turbulenceProperties`, `transportProperties`, `scale`) that the baseline doc must freeze.
- Found: `scripts/pipelines/stubs/stub_openfoam.py` — repo already has a synthetic OpenFOAM stub for higher-level pipeline validation, confirming there is currently no canonical operator-facing baseline workflow doc for real solver execution.
- Found: `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` — the baseline workflow package should satisfy the existing reusable-artifact bundle expectations for engineering delivery instead of inventing a parallel contract.
- Found: `examples/openfoam/cavity-v2312/` directory was created empty during v1 scaffold; the manifest README must still be authored.
- Gap: no repo-tracked OpenFOAM baseline runbook yet exists under `docs/engineering/portability/`.

### Bootstrap-path evidence (verified 2026-04-21)
- `scripts/openfoam/run-openfoam-tutorials.sh:10` — pinned default: `/usr/lib/openfoam/openfoam2312/etc/bashrc` (current runtime source of truth in code).
- `docs/research/openfoam-tutorials.md:27` — historical research note references `/opt/openfoam2312/etc/bashrc`.
- `docs/research/openfoam-tutorials.md:43,95,132,175` — operator tutorial commands use `source /usr/lib/... || source /opt/...` fallback form, confirming both paths appeared at different times in repo history.
- Host probe status: **NOT verified on dev-secondary for v2**. Neither `/usr/lib/openfoam/openfoam2312/etc/bashrc` nor `/opt/openfoam2312/etc/bashrc` exists on ace-linux-1 (this planning host; OpenFOAM is not installed here per `config/workstations/registry.yaml`). A live probe on dev-secondary (`ace-linux-2`) is therefore a **prerequisite of implementation**, not an assumption baked into policy. See §Decisions: bootstrap-path policy.

### Standards
| Standard | Status | Source |
|---|---|---|
| OpenFOAM portability baseline (ESI v2312 on dev-secondary) | done / normative baseline exists | `docs/engineering/portability/PORTABILITY_CONTRACT.md` |
| Engineering artifact portability / machine-role policy | done | `docs/engineering/portability/MACHINE_ROLES.md`, `config/workstations/registry.yaml` |
| Python invocation on Linux | normative | `AGENTS.md:14` ("Python: `uv run` always — never bare `python3`"), `.claude/memory/context.md:13-16` |
| External design-code implementation | not applicable for this issue | issue #2269 scope is tool/workflow standardization |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` — confirms the capability model: case setup, solver execution, failure diagnosis, validation against tutorial benchmarks, VTK/ParaView post-processing.

### Documents consulted
- GitHub issue #2269 — defines the portability baseline goal, required deliverables, and acceptance criteria.
- GitHub issue #25 — historical OpenFOAM capability issue (broader scope; this plan stays narrow).
- `docs/engineering/portability/PORTABILITY_CONTRACT.md` — locks OpenFOAM (ESI) v2312 on dev-secondary as canonical CFD baseline.
- `config/workstations/registry.yaml` — confirms dev-secondary (`ace-linux-2`) is the engineering execution machine with `openfoam`, `paraview`, `gmsh`, `tmux`, `uv` installed.
- `data/document-index/online-resource-registry.yaml` — contains both the upstream OpenFOAM core repo entry and the ESI/OpenCFD fork entry.
- `docs/document-intelligence/data-intelligence-map.md` and `docs/document-intelligence/README.md` — canonical intelligence surfaces.

### Gaps identified
- Gap: no repo-tracked baseline workflow doc currently states the exact OpenFOAM fork/version, environment bootstrap, runner commands, evidence artifacts, and failure modes for the workspace-hub engineering host.
- Gap: no canonical reproducible smoke-case manifest/example path currently exists (the `examples/openfoam/cavity-v2312/` dir is empty).
- Gap: current repo sources disagree on bootstrap path between `/usr/lib/...` (runner default) and `/opt/...` (research notes); implementation must **probe dev-secondary live**, pin the attested path, and normalize stale references.
- Gap: the v1-landed wrapper uses `python3` fallback in violation of `AGENTS.md:14`; must be reworked to `uv run python`.

<!-- Verification: distinct sources >= 3. Current count: 10 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` |
| Planning index row | `docs/plans/README.md` |
| Canonical baseline workflow doc | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` |
| Baseline validator wrapper (operator entrypoint) | `scripts/openfoam/verify-openfoam-baseline.sh` |
| Tutorial runner (internal execution engine) | `scripts/openfoam/run-openfoam-tutorials.sh` |
| Smoke-case manifest/example | `examples/openfoam/cavity-v2312/README.md` |
| Engineering delivery contract | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` |
| Plan review — Claude v2 self-review | `scripts/review/results/2026-04-21-plan-2269-claude-rev-2.md` |

---

## Deliverable

A repo-tracked OpenFOAM baseline package for dev-secondary that freezes ESI/OpenFOAM.com v2312 as the canonical fork/version, documents the exact workflow and failure modes, provides a repo-tracked smoke manifest for a mandatory `cavity` smoke run plus an optional `pitzDaily` benchmark, and exposes a deterministic operator-facing validator wrapper that emits explicit pass/fail YAML evidence to a standardized default path with optional caller override. Python invocations obey the repo `uv run` policy on Linux.

---

## Wrapper/Runner Contract

**Single-owner rule.** Bootstrap resolution, environment sourcing, and fork/version verification are owned **exclusively** by `verify-openfoam-baseline.sh`. `run-openfoam-tutorials.sh` is demoted to an internal execution engine that **requires** a prepared environment and never re-sources the bashrc.

### `verify-openfoam-baseline.sh` — operator entrypoint (owner)

Responsibilities (all must hold):
1. Probe candidate bootstrap paths in declared order; select the first that exists.
2. Source the selected bashrc; export `OPENFOAM_BASHRC_RESOLVED=<path>` for the runner to read.
3. Verify `WM_PROJECT_VERSION=v2312`, `foamVersion` stdout contains `2312`, and `WM_PROJECT_DIR` basename resolves to `openfoam2312`. On failure emit a `version-mismatch` failure verdict and exit non-zero.
4. Invoke the runner with an explicit contract: `--skip-bootstrap --tutorials <list> --verdict <raw-path>`. The `--skip-bootstrap` flag tells the runner it is inside a prepared environment and MUST NOT source any bashrc.
5. Normalize the runner's raw YAML to the final schema, adding wrapper-owned fields (`fork`, `version`, `verification_method`, `resolved_bashrc_path`).
6. Emit final YAML to the operator-specified path (default `logs/engineering/openfoam-baseline/latest-verdict.yaml`) and to the same path on failure (minimum failure schema).

Python invocation: `uv run python - <<'PY' ... PY` on Linux. A fallback to bare `python3` is **forbidden** — if `uv` is unavailable, the wrapper fails fast with an explicit `uv-missing` error. (Rationale: `AGENTS.md:14` normative rule. Windows execution is out of scope for this issue — the canonical host is dev-secondary, Linux.)

### `run-openfoam-tutorials.sh` — internal execution engine (delegate)

Responsibilities (all must hold):
1. Accept `--skip-bootstrap` as a required flag when invoked by the wrapper. Without `--skip-bootstrap`, the runner MAY source a bashrc (legacy standalone mode) — this path is deprecated and warned-about but not removed in this issue.
2. With `--skip-bootstrap`, trust `$WM_PROJECT_DIR`/`$WM_PROJECT_VERSION` as already set; do NOT call `source` on any bashrc.
3. Accept `--tutorials <csv>` and run exactly the listed tutorials.
4. Accept `--verdict <path>` and write raw YAML to it.
5. Emit rows for whatever tutorials it was asked to run; `damBreak` is filtered out by the wrapper, not the runner.

### Handoff envelope

| Environment variable | Set by | Read by | Purpose |
|---|---|---|---|
| `OPENFOAM_BASHRC_RESOLVED` | wrapper | runner (optional, logged) | Attests which bashrc the wrapper sourced |
| `WM_PROJECT_VERSION` | bashrc (sourced by wrapper) | wrapper (verification), runner (trust) | Canonical version string |
| `WM_PROJECT_DIR` | bashrc (sourced by wrapper) | wrapper (verification), runner (trust) | OpenFOAM install root |
| `OPENFOAM_BASHRC_PATHS` (test-only) | caller override | wrapper | Dependency-injection seam for fixture-based probe-order tests |

---

## Pseudocode

```text
inspect OpenFOAM research notes, issue #2269 acceptance criteria, existing runner, and portability/delivery contracts
lock the canonical baseline:
    machine = dev-secondary (ace-linux-2)
    fork = ESI / OpenFOAM.com
    version = v2312
    mandatory smoke case = cavity
    optional benchmark case = pitzDaily
    default verdict path = logs/engineering/openfoam-baseline/latest-verdict.yaml
prerequisite (implementation time, not plan time):
    operator runs `ls /usr/lib/openfoam/openfoam2312/etc/bashrc /opt/openfoam2312/etc/bashrc` on dev-secondary
    records attested path in implementation PR description
    updates workflow doc §Prerequisites with attested path as primary
wrapper flow (verify-openfoam-baseline.sh):
    probe bootstrap paths in fixed supported order:
        if OPENFOAM_BASHRC_PATHS is set (test-only): use that list
        otherwise use permanent supported list:
            1. /usr/lib/openfoam/openfoam2312/etc/bashrc       # matches runner default
            2. /opt/openfoam2312/etc/bashrc                    # historical research path
        first path that exists wins; record every attempted path
        if both exist: first in order wins; secondary logged as skipped
    if neither path exists: fail with explicit missing-bashrc error + write failure verdict
    source selected path; export OPENFOAM_BASHRC_RESOLVED
    verify fork/version:
        WM_PROJECT_VERSION must equal `v2312`
        foamVersion stdout must contain `2312`
        WM_PROJECT_DIR basename must resolve to `openfoam2312`
    verification_method field must be exactly:
        `WM_PROJECT_VERSION=v2312; foamVersion~2312; WM_PROJECT_DIR=<resolved_path>`
    if any check fails: exit non-zero + version-mismatch failure verdict
    invoke runner: bash run-openfoam-tutorials.sh --skip-bootstrap --tutorials <list> --verdict <raw-path>
    normalize raw YAML via `uv run python` (never `python3`):
        load raw YAML
        validate tutorial row types
        filter out damBreak
        add wrapper-owned fields (fork, version, verification_method, resolved_bashrc_path)
        write final YAML atomically
    on runner non-zero: surface stderr, write runner-failure verdict
runner flow (run-openfoam-tutorials.sh):
    accept --skip-bootstrap (trust env), --tutorials, --verdict
    if --skip-bootstrap: do NOT source bashrc; assume WM_PROJECT_* is set
    run selected tutorials; emit raw YAML; exit non-zero on any tutorial failure
YAML artifact contract:
    default path = logs/engineering/openfoam-baseline/latest-verdict.yaml
    wrapper creates parent dir if missing; logs/ is operational output, not git-tracked
    required top-level fields = generated_at, machine, resolved_bashrc_path, fork, version,
      verification_method, overall_verdict, tutorials
    required per-tutorial fields = name (str), status (enum PASS|FAIL|NOT_FOUND), time_directories (int >= 0)
    overall_verdict = enum PASS|FAIL
    failure verdict minimum schema = generated_at, machine, resolved_bashrc_path (if known),
      verification_method (if reached), overall_verdict=FAIL, tutorials (possibly empty),
      error_summary, error_message, attempted_bashrc_paths
    generated_at is the only volatile field
write baseline workflow doc recording:
    supported fork/version
    bootstrap path probe order + attested dev-secondary path
    mandatory smoke + optional benchmark
    exact YAML schema + default artifact path
    failure modes + troubleshooting (incl. `uv` absence)
create cavity-v2312 manifest (instructions-only, required headings = Overview, Prerequisites,
  Commands, Expected Outputs, Failure Modes):
    copy tutorial from $FOAM_TUTORIALS into run dir
    blockMesh then icoFoam
    point operators at canonical validator for routine checks
    do not commit copied tutorial case data
verify behavior via tests listed in §TDD Test List
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/plans/README.md` | align index/state with plan-review status |
| Create | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` | canonical operator-facing baseline workflow doc with traceable requirements coverage |
| Update | `scripts/openfoam/verify-openfoam-baseline.sh` | replace `python3` fallback with `uv run python` (fail fast if `uv` missing); wire to `--skip-bootstrap` runner call |
| Update | `scripts/openfoam/run-openfoam-tutorials.sh` | add `--skip-bootstrap` flag; make self-sourcing conditional and deprecated-warned; add `--tutorials` selection; remove `damBreak` from default set |
| Update | `docs/research/openfoam-tutorials.md` | normalize stale `/opt/openfoam2312/etc/bashrc` references to match attested dev-secondary path after live probe |
| Create | `examples/openfoam/cavity-v2312/README.md` | repo-tracked smoke-case manifest with required headings |
| Create | `tests/openfoam/test_verify_openfoam_baseline.py` | pytest harness; fixture-only schema tests + `@pytest.mark.openfoam` host-required tests; invoked via `uv run pytest` |
| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | add explicit cross-reference to the OpenFOAM baseline package |
| Update | `docs/README.md` | add discoverability link to canonical OpenFOAM baseline workflow |

---

## TDD Test List

All tests run via `uv run pytest` on Linux (never bare `python3`/`pytest`).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_verify_script_succeeds_and_emits_schema_valid_verdict` | validator succeeds in supported env, writes schema-valid YAML | `@pytest.mark.openfoam`, dev-secondary env | exit 0 + YAML with required typed fields |
| `test_verify_script_fails_when_bashrc_missing` | validator fails fast with explicit missing-bashrc error | `OPENFOAM_BASHRC_PATHS` overrides to nonexistent fixtures | non-zero + exact missing-bashrc message naming probe order |
| `test_verify_script_fails_fast_when_uv_missing` | wrapper refuses to degrade to bare `python3` when `uv` is absent | `PATH` stub without `uv` | non-zero + `uv-missing` error; no fallback attempted |
| `test_verify_script_surfaces_runner_failure` | validator does not mask delegated runner failures | stubbed runner returns non-zero via `OPENFOAM_TUTORIAL_RUNNER_PATH` override | non-zero + preserved runner stderr in verdict |
| `test_verify_script_records_fork_version_via_named_mechanism` | validator proves fork/version using `$WM_PROJECT_VERSION`, `foamVersion`, `$WM_PROJECT_DIR` | supported env or mocked version output | `verification_method` string in exact format |
| `test_verify_script_normalizes_final_yaml_contract` | wrapper emits final normalized schema | successful runner output fixture | top-level schema matches contract; only `generated_at` volatile |
| `test_verify_script_prefers_first_supported_bashrc_path` | dual-path installations follow deterministic precedence | two fixture bashrc paths exist | first path wins; secondary logged as skipped |
| `test_verify_script_rejects_invalid_benchmark_value` | wrapper fails fast on out-of-scope benchmark | `--benchmark badcase` | non-zero + unsupported-benchmark error naming allowed values |
| `test_runner_skip_bootstrap_does_not_source_bashrc` | runner honors the `--skip-bootstrap` wrapper contract | `run-openfoam-tutorials.sh --skip-bootstrap ...` with unset `OPENFOAM_BASHRC` | runner does not attempt to source; relies on injected `WM_PROJECT_*` |
| `test_manifest_instructions_do_not_commit_case_data` | smoke manifest is instructions-only | repo tree | `examples/openfoam/cavity-v2312/README.md` present with required headings; no committed case tree |
| `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc cross-references issue #2269 requirements | workflow doc text | explicit requirement-to-deliverable mapping |
| `test_pytest_harness_covers_validator_contract` | explicit pytest harness exists for validator behavior | repo tree | `tests/openfoam/test_verify_openfoam_baseline.py` exists with required cases |

---

## Acceptance Criteria

- [ ] Implementation commit description includes an attested live `ls` probe on dev-secondary showing which of `/usr/lib/openfoam/openfoam2312/etc/bashrc` and `/opt/openfoam2312/etc/bashrc` actually exists; workflow doc §Prerequisites records the attested primary path.
- [ ] `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` explicitly declares canonical fork/version, permanent two-path bootstrap support list + attested primary, both-paths-exist precedence, mandatory `cavity` smoke tier, optional `pitzDaily` benchmark tier, `damBreak` non-canonical status, default verdict path, `uv run` requirement, and troubleshooting for `uv` absence + bashrc absence + version mismatch.
- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` uses `uv run python` for all Python embedding; **no `python3` fallback**; fails fast with `uv-missing` error if `uv` is absent.
- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` emits schema-valid YAML with: `generated_at`, `machine`, `resolved_bashrc_path`, `fork`, `version`, exact `verification_method`, `overall_verdict`, typed tutorial rows. Only `generated_at` volatile.
- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` fails with explicit testable messages when neither supported bootstrap path exists; writes failure verdict with minimum schema; preserves delegated runner failures.
- [ ] `scripts/openfoam/run-openfoam-tutorials.sh` accepts and honors `--skip-bootstrap`; when invoked with `--skip-bootstrap` it does NOT source any bashrc; the wrapper ALWAYS invokes it with `--skip-bootstrap`.
- [ ] `examples/openfoam/cavity-v2312/README.md` is instructions-only; contains required headings (Overview, Prerequisites, Commands, Expected Outputs, Failure Modes); documents reproducible copy/run commands; commits no tutorial case data.
- [ ] `tests/openfoam/test_verify_openfoam_baseline.py` exists; uses `@pytest.mark.openfoam` for host-dependent tests; fixture-only schema tests run anywhere; covers dual-path probe + invalid-benchmark + missing-`uv` + `--skip-bootstrap` runner contract.
- [ ] Stale `/opt/openfoam2312/etc/bashrc` references in `docs/research/openfoam-tutorials.md` are normalized to match attested primary path.
- [ ] Baseline workflow is linked from `docs/README.md`.
- [ ] Workflow doc contains explicit traceability from issue #2269 requirements to deliverables/tests/acceptance criteria.

---

## Adversarial Review History

| Wave | Date | Provider | Verdict | Key findings |
|---|---|---|---|---|
| v1-wave1 | 2026-04-15 | Claude | MINOR | bootstrap-path both-exist policy, YAML handoff choice, pytest host strategy, `damBreak` status |
| v1-wave1 | 2026-04-15 | Codex | MAJOR | retrieval-backed runtime truth; failure-artifact policy; deterministic fixture language |
| v1-wave1 | 2026-04-15 | Gemini | MAJOR | dependency-injection/testability; YAML normalization mechanics; benchmark/runner handoff |
| v1-final | 2026-04-15 | all three | APPROVED (post-revision) | plan landed as status:plan-approved |
| v1-rollback | 2026-04-21 | Codex (fresh) | MAJOR | (1) `python3` violates `uv run` repo policy per `AGENTS.md:14` / `.claude/memory/context.md:13-16`; (2) bootstrap-path precedence frozen without live host probe; (3) wrapper/runner bootstrap ownership ambiguous — runner still self-sources |
| v1-rollback | 2026-04-21 | Gemini (fresh) | APPROVE w/ MINOR | PyYAML availability on dev-secondary; JSON alternative for intermediate handoff |

**v2 revision rationale (2026-04-21):**
- **Codex MAJOR #1 (`python3` policy)** → replaced all `python3` invocations with `uv run python` in pseudocode, acceptance criteria, TDD tests, and the Wrapper/Runner Contract. Added `test_verify_script_fails_fast_when_uv_missing` to enforce no-fallback. Added explicit `uv-missing` error path. Citation: `AGENTS.md:14`, `.claude/memory/context.md:13-16`.
- **Codex MAJOR #2 (unverified bootstrap)** → downgraded the two-path precedence from "permanent baseline decision" to a **supported fallback policy**, with the attested host-specific primary path required as an implementation-time live probe on dev-secondary, recorded in PR description and workflow doc §Prerequisites. Plan distinguishes `attested host reality` from `supported fallback policy`.
- **Codex MAJOR #3 (wrapper/runner ambiguity)** → added new §Wrapper/Runner Contract section defining single-owner rule (wrapper owns bootstrap/version; runner must honor `--skip-bootstrap`); added `test_runner_skip_bootstrap_does_not_source_bashrc`; made runner `--skip-bootstrap` flag mandatory in the wrapper's runner invocation.
- **Gemini MINOR (PyYAML availability)** → workflow doc troubleshooting must cover `ModuleNotFoundError: yaml` → `uv add pyyaml` inside the repo's tooling env. Intermediate JSON handoff deferred as a follow-up; for this issue the wrapper treats PyYAML as a `uv run` dependency.

---

## Requirement traceability

| Issue #2269 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
|---|---|---|---|
| declare target fork/version explicitly | workflow doc, wrapper | `test_verify_script_records_fork_version_via_named_mechanism` | workflow doc declares fork/version; validator records verification_method |
| canonical runner command(s) documented | workflow doc, manifest | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc + manifest provide operator-facing commands |
| minimal smoke case under reproducible repo-tracked path | `examples/openfoam/cavity-v2312/README.md` | `test_manifest_instructions_do_not_commit_case_data` | instructions-only reproducible path with explicit copy/run commands |
| validator produces pass/fail output with explicit checks | wrapper, pytest harness | `test_verify_script_succeeds_..._verdict`, `_surfaces_runner_failure`, `_normalizes_final_yaml_contract` | schema-valid pass/fail YAML; root-cause preservation |
| common failure modes and mismatches documented | workflow doc, research doc | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc troubleshooting; stale paths normalized |
| workflow executable on canonical engineering host with documented prerequisites | workflow doc, wrapper | `test_verify_script_succeeds_..._verdict`, `_fails_when_bashrc_missing`, `_fails_fast_when_uv_missing` | success + failure behavior pinned for dev-secondary |
| validator/benchmark path clarity | workflow doc, wrapper | `test_workflow_doc_covers_traceable_issue_requirements`, `_rejects_invalid_benchmark_value` | `pitzDaily` benchmark trigger; `damBreak` non-canonical |
| wrapper/runner separation of concerns | wrapper, runner, Wrapper/Runner Contract | `test_runner_skip_bootstrap_does_not_source_bashrc` | runner honors `--skip-bootstrap`; single-owner bootstrap |
| repo-compliant Python invocation | wrapper, workflow doc troubleshooting | `test_verify_script_fails_fast_when_uv_missing` | `uv run` on Linux; no `python3` fallback |

---

## Risks

- **Risk:** issue #25 claims broad capability completion in digitalmodel while #2269 is a narrower portability/documentation slice; implementation must avoid reopening broader scope.
- **Risk:** repo sources disagree on bootstrap path; implementation must normalize stale references while preserving the supported two-path fallback contract.
- **Risk:** current runner executes `damBreak` in addition to `cavity`; baseline workflow keeps `damBreak` explicitly outside the canonical acceptance contract unless promoted later.
- **Risk:** `uv` must be present on dev-secondary. `config/workstations/registry.yaml:41` lists `uv` in dev-secondary tools, but the workflow doc must still document the failure mode and recovery command.
- **Risk:** live host probe of the bashrc path requires operator access to dev-secondary; if the planning agent lacks that access, implementation must pause for operator confirmation before landing the attested primary path in the workflow doc.

## Decisions

- **Decision:** Python invocation on Linux = `uv run python` only; no `python3` fallback. Per `AGENTS.md:14` + `.claude/memory/context.md:13-16`.
- **Decision:** bootstrap policy is a two-path **supported fallback list** — `/usr/lib/openfoam/openfoam2312/etc/bashrc` first, `/opt/openfoam2312/etc/bashrc` second — with the **attested primary** recorded at implementation time via live probe on dev-secondary.
- **Decision:** if both supported paths exist, first in probe order wins; second is logged as skipped.
- **Decision:** single-owner bootstrap — wrapper owns bashrc probing/sourcing/version verification; runner honors `--skip-bootstrap` and never self-sources when invoked by the wrapper.
- **Decision:** mandatory fast smoke tier = `cavity`.
- **Decision:** optional deeper benchmark tier = `pitzDaily`, invoked only via explicit wrapper flag `--benchmark pitzDaily`.
- **Decision:** invalid benchmark values fail fast with an unsupported-benchmark error naming allowed values.
- **Decision:** `damBreak` stays available in the delegated runner for broader execution coverage but is filtered out of canonical baseline output by the wrapper.
- **Decision:** default verdict path = `logs/engineering/openfoam-baseline/latest-verdict.yaml`; optional caller override via `--verdict`.
- **Decision:** example manifest is instruction-only; must not commit copied tutorial case data.
- **Decision:** discoverability target is `docs/README.md`.
- **Decision:** host-required validator tests use `@pytest.mark.openfoam`; fixture-only schema/normalization tests run on any host via `uv run pytest`.

---

## Complexity: T2

**T2** — bounded documentation + validation standardization across a small set of repo files, with one existing script to refine (`run-openfoam-tutorials.sh`), one existing wrapper scaffold to correct (`verify-openfoam-baseline.sh`), and one new deterministic manifest/example path to add.
