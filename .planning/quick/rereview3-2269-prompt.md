# Adversarial Re-Review Request: Issue #2269 (wave 3)

Review the CURRENT plan text only after the latest patch wave. Be adversarial and concrete. Identify any remaining unresolved blockers, hidden implementation decisions, weak retrieval, non-falsifiable acceptance criteria/tests, governance drift, or approval-readiness gaps.

Return exactly these sections:
1. Overall verdict: APPROVE | MINOR | MAJOR
2. Ready for user approval: Yes | No
3. Retrieval adequacy: adequate | insufficient
4. Top blockers
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Plan under review:

```markdown
     1|# Plan for #2269: standardize OpenFOAM v2312 baseline workflow and validation
     2|
     3|> **Status:** plan-review
     4|> **Complexity:** T2
     5|> **Date:** 2026-04-15
     6|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2269
     7|> **Review artifacts:** scripts/review/results/2026-04-15-plan-2269-claude.md | scripts/review/results/2026-04-15-plan-2269-codex.md | scripts/review/results/2026-04-15-plan-2269-gemini.md
     8|
     9|---
    10|
    11|## Resource Intelligence Summary
    12|
    13|### Existing repo code
    14|- Found: `scripts/openfoam/run-openfoam-tutorials.sh` — current CLI contract is `bash scripts/openfoam/run-openfoam-tutorials.sh [--verdict /path/to/verdict.yaml]`; it sources `/usr/lib/openfoam/openfoam2312/etc/bashrc`, runs `cavity` and `damBreak`, writes YAML with `generated_at`, `machine`, `openfoam_version`, `overall_verdict`, and per-tutorial status/time-directory counts, and exits non-zero on failure. This is the strongest existing execution engine to reuse underneath a new operator-facing validator.
    15|- Found: `docs/research/openfoam-tutorials.md` — repo research records that OpenFOAM ESI v2312 is installed on dev-secondary, that `pitzDaily` converged in 281 iterations, and that `cavity`/`damBreak` were later completed headlessly; this provides both a fast smoke-case candidate (`cavity`) and a stronger benchmark candidate (`pitzDaily`) with known expected behavior.
    16|- Found: `docs/research/openfoam-version-landscape.md` — explicitly recommends the ESI/OpenFOAM.com fork with v2312 syntax for dev-secondary and documents fork-specific dict differences (`turbulenceProperties`, `transportProperties`, `scale`) that the baseline doc must freeze.
    17|- Found: `scripts/pipelines/stubs/stub_openfoam.py` — repo already has a synthetic OpenFOAM stub for higher-level pipeline validation, confirming there is currently no canonical operator-facing baseline workflow doc for real solver execution.
    18|- Found: `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` — the baseline workflow package should satisfy the existing reusable-artifact bundle expectations for engineering delivery instead of inventing a parallel contract.
    19|- Gap: no canonical plan artifact existed yet for #2269 under `docs/plans/` before this draft.
    20|- Gap: no repo-tracked OpenFOAM baseline runbook exists under `docs/engineering/portability/`, and no reproducible smoke-case manifest/example path currently exists in the repo.
    21|
    22|### Standards
    23|| Standard | Status | Source |
    24||---|---|---|
    25|| OpenFOAM portability baseline (ESI v2312 on dev-secondary) | done / normative baseline exists | `docs/engineering/portability/PORTABILITY_CONTRACT.md` |
    26|| Engineering artifact portability / machine-role policy | done | `docs/engineering/portability/MACHINE_ROLES.md`, `config/workstations/registry.yaml` |
    27|| External design-code implementation | not applicable for this issue | issue #2269 scope is tool/workflow standardization, not a DNV/API calculation implementation |
    28|
    29|### LLM Wiki pages consulted
    30|- `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` — existing engineering wiki page confirms the capability model: case setup, solver execution, failure diagnosis, validation against tutorial benchmarks, and VTK/ParaView post-processing.
    31|
    32|### Documents consulted
    33|- GitHub issue #2269 — defines the portability baseline goal, required deliverables, and acceptance criteria for standardizing the OpenFOAM workflow.
    34|- GitHub issue #25 — historical OpenFOAM capability issue showing the broader digitalmodel/OpenFOAM capability exists, but documentation remained deferred; #2269 is the bounded portability/documentation/validation follow-on.
    35|- `docs/engineering/portability/PORTABILITY_CONTRACT.md` — locks OpenFOAM (ESI) v2312 on dev-secondary as the canonical CFD baseline and defines which artifacts must become repo-tracked portable knowledge.
    36|- `config/workstations/registry.yaml` — confirms dev-secondary (`ace-linux-2`) is the engineering execution machine with `openfoam`, `paraview`, `gmsh`, and `tmux` installed.
    37|- `data/document-index/online-resource-registry.yaml` — contains both the upstream OpenFOAM core repo entry and the ESI/OpenCFD fork entry, reinforcing that the plan should document which fork/baseline this repo standardizes.
    38|- `docs/document-intelligence/data-intelligence-map.md` and `docs/document-intelligence/README.md` — confirm where engineering registries and intelligence entry points live for future discoverability, so the baseline plan can anchor its sources to the canonical intelligence surfaces.
    39|
    40|### Gaps identified
    41|- Gap: no canonical local plan exists for #2269.
    42|- Gap: no repo-tracked baseline workflow doc currently states the exact OpenFOAM fork/version, environment bootstrap, runner commands, evidence artifacts, and failure modes for the workspace-hub engineering host.
    43|- Gap: no canonical reproducible smoke-case manifest/example path currently exists in the repo for OpenFOAM baseline validation.
    44|- Gap: the current sources disagree on bootstrap path (`/usr/lib/openfoam/openfoam2312/etc/bashrc` in the runner vs `/opt/openfoam2312/etc/bashrc` in research notes), so implementation must normalize the incorrect source after live verification rather than leaving both as active truths.
    45|- Gap: existing `run-openfoam-tutorials.sh` is useful but not yet framed as the canonical operator-facing baseline validator with explicit prerequisites, output path contract, and failure-mode guidance.
    46|
    47|<!-- Verification: distinct sources >= 3. Current count: 9 -->
    48|
    49|---
    50|
    51|## Artifact Map
    52|
    53|| Artifact | Path |
    54||---|---|
    55|| This plan | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` |
    56|| Planning index row | `docs/plans/README.md` |
    57|| Canonical baseline workflow doc | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` |
    58|| Baseline validator wrapper | `scripts/openfoam/verify-openfoam-baseline.sh` |
    59|| Existing tutorial runner / execution engine | `scripts/openfoam/run-openfoam-tutorials.sh` |
    60|| Smoke-case manifest/example | `examples/openfoam/cavity-v2312/README.md` |
    61|| Engineering delivery contract | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` |
    62|| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2269-claude.md` |
    63|| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2269-codex.md` |
    64|| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2269-gemini.md` |
    65|
    66|---
    67|
    68|## Deliverable
    69|
    70|A repo-tracked OpenFOAM baseline package for dev-secondary that freezes ESI/OpenFOAM.com v2312 as the canonical fork/version, documents the exact workflow and failure modes, provides a repo-tracked smoke manifest for a mandatory `cavity` smoke run plus an optional `pitzDaily` benchmark, and exposes a deterministic validator wrapper that emits explicit pass/fail YAML evidence to a standardized default path with optional caller override.
    71|
    72|---
    73|
    74|## Pseudocode
    75|
    76|```text
    77|inspect existing OpenFOAM research notes, issue #2269 acceptance criteria, the existing tutorial runner, and the portability/delivery contracts
    78|lock the canonical baseline:
    79|    machine = dev-secondary
    80|    fork = ESI / OpenFOAM.com
    81|    version = v2312
    82|    mandatory smoke case = cavity
    83|    optional benchmark case = pitzDaily
    84|    default verdict path = logs/engineering/openfoam-baseline/latest-verdict.yaml
    85|probe bootstrap paths in fixed order using:
    86|    OPENFOAM_BASHRC_PATHS if set (colon-separated for tests)
    87|    otherwise the permanent supported baseline list:
    88|        1. /usr/lib/openfoam/openfoam2312/etc/bashrc
    89|        2. /opt/openfoam2312/etc/bashrc
    90|    record every attempted path in stderr/log context
    91|    if both baseline paths exist:
    92|        first path in probe order wins
    93|        log that the secondary path was skipped
    94|    source the selected path
    95|    run `foamVersion` and inspect `$WM_PROJECT_DIR`
    96|    parse rule:
    97|        foamVersion stdout must equal `OpenFOAM-v2312`
    98|        WM_PROJECT_DIR basename must resolve to `openfoam2312`
    99|    verification_method field must be exactly:
   100|        `foamVersion=OpenFOAM-v2312; WM_PROJECT_DIR=<resolved_path>`
   101|    if either check fails: exit non-zero with explicit version-mismatch error
   102|    if neither path exists: fail with explicit missing-bashrc error and no silent fallback
   103|responsibility split:
   104|    run-openfoam-tutorials.sh remains the execution engine for tutorial runs, current tutorial-specific status rows, and raw tutorial verdict generation
   105|    verify-openfoam-baseline.sh becomes the only operator-facing entrypoint; it resolves bootstrap path, verifies fork/version via `foamVersion` and `$WM_PROJECT_DIR`, chooses output path, invokes the runner, and emits the final normalized YAML artifact
   106|YAML artifact contract:
   107|    default path = logs/engineering/openfoam-baseline/latest-verdict.yaml
   108|    optional override flag `--verdict` redirects output and must be forwarded to the delegated runner output path contract
   109|    required top-level fields = generated_at, machine, resolved_bashrc_path, fork, version, verification_method, overall_verdict, tutorials
   110|    required `tutorials` structure = list of objects, for example:
   111|        tutorials:
   112|          - name: cavity
   113|            status: PASS
   114|            time_directories: 501
   115|    required per-tutorial fields =
   116|        name: string
   117|        status: enum PASS|FAIL|NOT_FOUND
   118|        time_directories: integer >= 0
   119|    overall_verdict: enum PASS|FAIL
   120|    generated_at is the only allowed volatile field; all others must be deterministic for a fixed environment/result
   121|    wrapper owns final artifact schema even if it imports tutorial rows from the runner
   122|YAML handoff strategy:
   123|    wrapper invokes runner with a temporary verdict path
   124|    wrapper uses an embedded Python snippet (not bash-native YAML editing) to load runner YAML, validate tutorial rows, add wrapper-owned fields, and write the final normalized artifact
   125|write a baseline workflow doc that records:
   126|    supported fork/version
   127|    bootstrap path contract and probe order
   128|    mandatory smoke case plus optional benchmark case
   129|    exact YAML verdict schema and default artifact location
   130|    failure modes and troubleshooting guidance
   131|create a repo-tracked smoke manifest/example path for cavity-v2312 that documents exact reproducible commands:
   132|    copy from the system tutorial into a temp/run directory
   133|    run blockMesh then icoFoam
   134|    point operators to the canonical validator for routine checks
   135|    do not commit copied tutorial case data
   136|verify behavior:
   137|    validator succeeds in supported env and produces schema-valid YAML verdict
   138|    validator fails with explicit message when bootstrap path is missing
   139|    validator surfaces delegated runner failure without masking root cause
   140|    validator records exact verification_method content
   141|    optional benchmark runs only when wrapper is invoked with `--benchmark pitzDaily`
   142|    damBreak remains runner-internal coverage and is not part of the canonical baseline acceptance contract unless explicitly promoted later
   143|```
   144|
   145|---
   146|
   147|## Files to Change
   148|
   149|| Action | Path | Reason |
   150||---|---|---|
   151|| Update | `docs/plans/README.md` | keep local plan index/state aligned with actual review state |
   152|| Create | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` | canonical operator-facing baseline workflow doc with traceable requirements coverage |
   153|| Create | `scripts/openfoam/verify-openfoam-baseline.sh` | operator-facing wrapper that resolves bootstrap path, verifies version, and emits normalized YAML verdicts |
   154|| Update | `scripts/openfoam/run-openfoam-tutorials.sh` | keep existing execution engine but tighten/declare its CLI and verdict schema contract |
   155|| Update | `docs/research/openfoam-tutorials.md` | normalize any stale bootstrap-path claim after live verification so research docs stop disagreeing with the canonical validator contract |
   156|| Create | `examples/openfoam/cavity-v2312/README.md` | repo-tracked smoke-case manifest/example path using tutorial-copy instructions rather than committed case data |
   157|| Create | `tests/openfoam/test_verify_openfoam_baseline.py` | behavioral pytest harness for validator success/failure/schema coverage |
   158|| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | link or cross-reference the OpenFOAM baseline package if needed for discoverability/contract alignment |
   159|| Update | `docs/README.md` | add discoverability link to the canonical OpenFOAM baseline workflow if the portability section does not already expose it |
   160|
   161|---
   162|
   163|## TDD Test List
   164|
   165|| Test name | What it verifies | Expected input | Expected output |
   166||---|---|---|---|
   167|| `test_verify_script_succeeds_and_emits_schema_valid_verdict` | validator succeeds in a supported environment and writes schema-valid YAML to the default path or explicit override path | supported dev-secondary environment | exit 0 + YAML containing required typed fields and normalized tutorial rows |
   168|| `test_verify_script_fails_when_bashrc_missing` | validator fails fast with explicit missing-bashrc error when neither supported bootstrap path exists | test override `OPENFOAM_BASHRC_PATHS` points to nonexistent fixtures | non-zero exit + exact missing-bashrc message naming probe order |
   169|| `test_verify_script_surfaces_runner_failure` | validator does not mask delegated tutorial-runner failures | runner returns non-zero via fixture/stubbed temp verdict path | non-zero exit + preserved runner failure reason in stderr/log/verdict |
   170|| `test_verify_script_records_fork_version_via_named_mechanism` | validator proves reported fork/version using `foamVersion` plus `$WM_PROJECT_DIR` | supported environment or mocked version command output | verdict records exact `verification_method` string format |
   171|| `test_verify_script_normalizes_final_yaml_contract` | wrapper emits the final normalized YAML schema even when reusing runner-produced tutorial rows | successful wrapped runner output fixture | top-level schema matches canonical contract, tutorial rows match typed constraints, and only `generated_at` is volatile |
   172|| `test_verify_script_prefers_first_supported_bashrc_path` | dual-path installations follow the permanent two-path baseline policy deterministically | two fixture bashrc paths exist in probe order | first path wins and secondary path is logged as skipped |
   173|| `test_manifest_instructions_do_not_commit_case_data` | smoke manifest is documentation/instructions only, not a committed tutorial case copy | repo tree | `examples/openfoam/cavity-v2312/README.md` present and no copied OpenFOAM case tree under the example path |
   174|| `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc cross-references issue #2269 requirements, default artifact path, smoke/benchmark tiers, troubleshooting contract, benchmark trigger, and `damBreak` status | workflow doc text | explicit requirement-to-deliverable mapping table/checklist |
   175|| `test_pytest_harness_covers_validator_contract` | the repo contains an explicit pytest harness for validator behavior and schema checks | repo tree | `tests/openfoam/test_verify_openfoam_baseline.py` exists with validator-oriented cases plus `@pytest.mark.openfoam` / fixture-only split |
   176|
   177|---
   178|
   179|## Acceptance Criteria
   180|
   181|- [ ] `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` explicitly declares the canonical fork/version, machine, permanent two-path bootstrap baseline, both-paths-exist policy, mandatory `cavity` smoke tier, optional `pitzDaily` benchmark tier, benchmark trigger mechanism, `damBreak` runner-only status, default verdict path, and troubleshooting guidance.
   182|- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` succeeds in a supported environment and emits schema-valid YAML evidence containing exact required fields: `generated_at`, `machine`, `resolved_bashrc_path`, `fork`, `version`, `verification_method`, `overall_verdict`, and typed tutorial result rows; only `generated_at` may remain volatile.
   183|- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` fails with explicit, testable messaging when neither supported bootstrap path exists, records the attempted probe order, and surfaces delegated runner failures without masking the root cause.
   184|- [ ] `examples/openfoam/cavity-v2312/README.md` exists as a manifest/instructions surface only; it does not commit copied tutorial case data into git and explicitly documents the reproducible tutorial-copy commands.
   185|- [ ] `tests/openfoam/test_verify_openfoam_baseline.py` exists and serves as the explicit pytest harness for validator success/failure/schema behavior, with `@pytest.mark.openfoam` for host-dependent tests, fixture-only schema tests runnable anywhere, and a test for dual-path probe determinism.
   186|- [ ] The implementation explicitly documents and preserves the responsibility split between `verify-openfoam-baseline.sh` (wrapper/final YAML owner using embedded Python normalization) and `run-openfoam-tutorials.sh` (execution engine/raw tutorial results).
   187|- [ ] Any stale bootstrap-path claim in `docs/research/openfoam-tutorials.md` or the runner is normalized so repo sources no longer disagree about the supported path contract.
   188|- [ ] The new baseline workflow is linked from `docs/README.md` so the canonical workflow is not stranded as a leaf file.
   189|- [ ] The workflow doc contains explicit traceability from issue #2269 requirements to deliverables/tests/acceptance criteria.
   190|
   191|---
   192|
   193|## Adversarial Review Summary
   194|
   195|| Provider | Verdict | Key findings |
   196||---|---|---|
   197|| Claude | MINOR | bootstrap-path both-exist policy, YAML handoff choice, pytest host strategy, and `damBreak` status needed tightening |
   198|| Codex | MAJOR | exact verification mechanism, final YAML schema completeness, deterministic test fixtures, and stricter runtime-truth pinning still required |
   199|| Gemini | MAJOR | dependency injection for bootstrap-path testing, explicit YAML normalization mechanism, and benchmark-trigger clarity still required |
   200|
   201|**Overall result:** FAIL — still not approval-ready. Wave 2 improved the plan materially, but unresolved MAJOR findings remain around final runtime-truth pinning, YAML schema/normalization mechanics, deterministic testability, and exact benchmark/runner-scope behavior.
   202|
   203|Revisions made based on wave-2 review:
   204|- added both-paths-exist bootstrap policy with version-mismatch guard
   205|- pinned fork/version verification to `foamVersion` plus `$WM_PROJECT_DIR`
   206|- chose an explicit YAML handoff strategy: wrapper uses embedded Python to normalize runner-produced YAML
   207|- defined `tutorials` structure and per-row field constraints
   208|- added dependency-injection language for bootstrap-path testing via `OPENFOAM_BASHRC_PATHS`
   209|- made pytest host strategy explicit (`@pytest.mark.openfoam` + fixture-only schema tests)
   210|- clarified benchmark trigger as an explicit wrapper flag and called out `damBreak` as runner-internal unless promoted
   211|- separated Risks from Decisions for cleaner governance state
   212|
   213|---
   214|
   215|## Requirement traceability
   216|
   217|| Issue #2269 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
   218||---|---|---|---|
   219|| declare target fork/version explicitly | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_verify_script_records_fork_version_via_named_mechanism` | baseline workflow doc declares fork/version; validator records verification mechanism |
   220|| canonical runner command(s) documented | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `examples/openfoam/cavity-v2312/README.md` | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc + manifest provide operator-facing commands |
   221|| minimal smoke case under reproducible repo-tracked path | `examples/openfoam/cavity-v2312/README.md` | `test_manifest_instructions_do_not_commit_case_data` | manifest exists as instruction-only reproducible path with explicit copy/run commands |
   222|| validator produces pass/fail output with explicit checks | `scripts/openfoam/verify-openfoam-baseline.sh`, `tests/openfoam/test_verify_openfoam_baseline.py` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_surfaces_runner_failure`, `test_verify_script_normalizes_final_yaml_contract` | validator emits schema-valid pass/fail YAML and preserves root-cause failure behavior |
   223|| common failure modes and version/fork mismatches documented | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `docs/research/openfoam-tutorials.md` | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc contains troubleshooting + stale path claims normalized |
   224|| workflow executable on canonical engineering host with documented prerequisites | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_fails_when_bashrc_missing` | success and failure behavior both pinned for dev-secondary |
   225|| validator/common benchmark path clarity | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_workflow_doc_covers_traceable_issue_requirements` | wrapper documents how optional `pitzDaily` benchmark is invoked and clarifies `damBreak` is runner-internal/non-canonical baseline scope unless explicitly promoted |
   226|
   227|---
   228|
   229|## Risks
   230|
   231|- **Risk:** issue #25 claims broad capability completion in digitalmodel while #2269 is a narrower portability/documentation slice; the implementation must avoid reopening the larger capability scope.
   232|- **Risk:** current repo sources disagree on bootstrap path; implementation must normalize stale references while preserving the permanent supported two-path baseline contract.
   233|- **Risk:** the current runner executes `damBreak` in addition to `cavity`; the baseline workflow must keep `damBreak` explicitly outside the canonical acceptance contract unless promoted in a later change.
   234|
   235|## Decisions
   236|
   237|- **Decision:** permanent supported bootstrap baseline = `/usr/lib/openfoam/openfoam2312/etc/bashrc` first, `/opt/openfoam2312/etc/bashrc` second.
   238|- **Decision:** if both supported paths exist, the first in probe order wins and the second is logged as skipped.
   239|- **Decision:** mandatory fast smoke tier = `cavity`.
   240|- **Decision:** optional deeper benchmark tier = `pitzDaily`, invoked only via explicit wrapper flag `--benchmark pitzDaily`.
   241|- **Decision:** `damBreak` may remain in the delegated runner for broader execution coverage, but it is not part of the canonical baseline acceptance contract for #2269.
   242|- **Decision:** default verdict path = `logs/engineering/openfoam-baseline/latest-verdict.yaml`, with optional caller override via CLI flag `--verdict` for ad hoc runs.
   243|- **Decision:** example manifest remains instruction-only and must not commit copied tutorial case data into git.
   244|- **Decision:** discoverability target is `docs/README.md` explicitly.
   245|
   246|---
   247|
   248|## Complexity: T2
   249|
   250|**T2** — bounded documentation + validation standardization across a small set of repo files, with one existing script to refine and one new deterministic wrapper/example path to add.
   251|
```
