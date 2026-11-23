# Adversarial Re-Review Request: Issue #2269

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
    85|probe bootstrap paths in fixed order:
    86|    1. /usr/lib/openfoam/openfoam2312/etc/bashrc
    87|    2. /opt/openfoam2312/etc/bashrc
    88|    record every attempted path in stderr/log context
    89|    if neither exists: fail with explicit missing-bashrc error and no silent fallback
    90|responsibility split:
    91|    run-openfoam-tutorials.sh remains the execution engine for tutorial runs, current tutorial-specific status rows, and raw tutorial verdict generation
    92|    verify-openfoam-baseline.sh becomes the only operator-facing entrypoint; it resolves bootstrap path, verifies fork/version via a named command/mechanism, chooses output path, invokes the runner, and emits the final normalized YAML artifact
    93|YAML artifact contract:
    94|    default path = logs/engineering/openfoam-baseline/latest-verdict.yaml
    95|    optional override flag may redirect output
    96|    required top-level fields = generated_at, machine, resolved_bashrc_path, fork, version, verification_method, overall_verdict, tutorials
    97|    generated_at is allowed volatile metadata; all other schema fields must be deterministic for a fixed environment/result
    98|    wrapper owns final artifact schema even if it imports tutorial rows from the runner
    99|write a baseline workflow doc that records:
   100|    supported fork/version
   101|    bootstrap path contract and probe order
   102|    mandatory smoke case plus optional benchmark case
   103|    exact YAML verdict schema and default artifact location
   104|    failure modes and troubleshooting guidance
   105|create a repo-tracked smoke manifest/example path for cavity-v2312 that documents tutorial-copy commands and expected outputs without committing copied case data
   106|verify behavior:
   107|    validator succeeds in supported env and produces schema-valid YAML verdict
   108|    validator fails with explicit message when bootstrap path is missing
   109|    validator surfaces delegated runner failure without masking root cause
   110|    validator records how fork/version was verified (named command/mechanism)
   111|```
   112|
   113|---
   114|
   115|## Files to Change
   116|
   117|| Action | Path | Reason |
   118||---|---|---|
   119|| Update | `docs/plans/README.md` | keep local plan index/state aligned with actual review state |
   120|| Create | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` | canonical operator-facing baseline workflow doc with traceable requirements coverage |
   121|| Create | `scripts/openfoam/verify-openfoam-baseline.sh` | operator-facing wrapper that resolves bootstrap path, verifies version, and emits normalized YAML verdicts |
   122|| Update | `scripts/openfoam/run-openfoam-tutorials.sh` | keep existing execution engine but tighten/declare its CLI and verdict schema contract |
   123|| Update | `docs/research/openfoam-tutorials.md` | normalize any stale bootstrap-path claim after live verification so research docs stop disagreeing with the canonical validator contract |
   124|| Create | `examples/openfoam/cavity-v2312/README.md` | repo-tracked smoke-case manifest/example path using tutorial-copy instructions rather than committed case data |
   125|| Create | `tests/openfoam/test_verify_openfoam_baseline.py` | behavioral pytest harness for validator success/failure/schema coverage |
   126|| Update | `docs/engineering/portability/ENGINEERING_DELIVERY_CHECKLIST.md` | link or cross-reference the OpenFOAM baseline package if needed for discoverability/contract alignment |
   127|| Update | `docs/README.md` | add discoverability link to the canonical OpenFOAM baseline workflow if the portability section does not already expose it |
   128|
   129|---
   130|
   131|## TDD Test List
   132|
   133|| Test name | What it verifies | Expected input | Expected output |
   134||---|---|---|---|
   135|| `test_verify_script_succeeds_and_emits_schema_valid_verdict` | validator succeeds in a supported environment and writes schema-valid YAML to the default path or explicit override path | supported dev-secondary environment | exit 0 + YAML containing `generated_at`, `machine`, `resolved_bashrc_path`, `fork`, `version`, `verification_method`, `overall_verdict`, and tutorial result rows |
   136|| `test_verify_script_fails_when_bashrc_missing` | validator fails fast with explicit missing-bashrc error when neither supported bootstrap path exists | hidden/invalid bootstrap paths | non-zero exit + exact missing-bashrc message naming probe order |
   137|| `test_verify_script_surfaces_runner_failure` | validator does not mask delegated tutorial-runner failures | runner returns non-zero | non-zero exit + preserved runner failure reason in stderr/log/verdict |
   138|| `test_verify_script_records_fork_version_via_named_mechanism` | validator proves reported fork/version using a documented command/mechanism | supported environment | verdict records the named verification command or source used |
   139|| `test_verify_script_normalizes_final_yaml_contract` | wrapper emits the final normalized YAML schema even when reusing runner-produced tutorial rows | successful wrapped runner output | top-level schema matches the canonical contract and only `generated_at` is volatile |
   140|| `test_manifest_instructions_do_not_commit_case_data` | smoke manifest is documentation/instructions only, not a committed tutorial case copy | repo tree | `examples/openfoam/cavity-v2312/README.md` present and no copied OpenFOAM case tree under the example path |
   141|| `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc cross-references issue #2269 requirements, default artifact path, smoke/benchmark tiers, and troubleshooting contract | workflow doc text | explicit requirement-to-deliverable mapping table/checklist |
   142|| `test_pytest_harness_covers_validator_contract` | the repo contains an explicit pytest harness for validator behavior and schema checks | repo tree | `tests/openfoam/test_verify_openfoam_baseline.py` exists with validator-oriented cases |
   143|
   144|---
   145|
   146|## Acceptance Criteria
   147|
   148|- [ ] `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` explicitly declares the canonical fork/version, machine, ordered bootstrap probe paths, mandatory `cavity` smoke tier, optional `pitzDaily` benchmark tier, default verdict path, and troubleshooting guidance.
   149|- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` succeeds in a supported environment and emits schema-valid YAML evidence containing exact required fields: `generated_at`, `machine`, `resolved_bashrc_path`, `fork`, `version`, `verification_method`, `overall_verdict`, and tutorial result rows; only `generated_at` may remain volatile.
   150|- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` fails with explicit, testable messaging when neither supported bootstrap path exists, records the attempted probe order, and surfaces delegated runner failures without masking the root cause.
   151|- [ ] `examples/openfoam/cavity-v2312/README.md` exists as a manifest/instructions surface only; it does not commit copied tutorial case data into git.
   152|- [ ] `tests/openfoam/test_verify_openfoam_baseline.py` exists and serves as the explicit pytest harness for validator success/failure/schema behavior.
   153|- [ ] The implementation explicitly documents and preserves the responsibility split between `verify-openfoam-baseline.sh` (wrapper/final YAML owner) and `run-openfoam-tutorials.sh` (execution engine/raw tutorial results).
   154|- [ ] Any stale bootstrap-path claim in `docs/research/openfoam-tutorials.md` or the runner is normalized so repo sources no longer disagree about the supported path contract.
   155|- [ ] The new baseline workflow is linked from an existing discoverability surface (`docs/README.md` or equivalent portability index) so the canonical workflow is not stranded as a leaf file.
   156|- [ ] The workflow doc contains explicit traceability from issue #2269 requirements to deliverables/tests/acceptance criteria.
   157|
   158|---
   159|
   160|## Adversarial Review Summary
   161|
   162|| Provider | Verdict | Key findings |
   163||---|---|---|
   164|| Claude | MAJOR | bootstrap-path contradiction unresolved; wrapper-vs-runner responsibility split unclear; example manifest scope must stay instruction-only |
   165|| Codex | MAJOR | smoke/benchmark scope and default artifact path must be decided explicitly; bashrc probe contract, YAML schema, and behavioral tests need tighter definition |
   166|| Gemini | MAJOR | YAML ownership contract, test harness, bashrc probing algorithm, and smoke-tier decision require explicit closure |
   167|
   168|**Overall result:** FAIL — not approval-ready. The plan now has full three-provider review coverage, but unresolved MAJOR findings remain around bootstrap-path precision, wrapper-vs-runner contract clarity, smoke/benchmark scope, YAML artifact schema, and behavioral testability.
   169|
   170|Revisions made based on review:
   171|- expanded retrieval to capture the current CLI/output-schema contract of `run-openfoam-tutorials.sh`
   172|- added `ENGINEERING_DELIVERY_CHECKLIST.md` to the evidence base
   173|- resolved the smoke-tier decision: mandatory `cavity`, optional `pitzDaily`
   174|- resolved the default artifact-path decision: `logs/engineering/openfoam-baseline/latest-verdict.yaml` with optional override
   175|- replaced the vague bashrc-risk wording with an explicit ordered probe contract
   176|- rewrote the TDD section toward falsifiable validator behavior and exact YAML fields
   177|- made discoverability and requirement traceability explicit acceptance criteria
   178|
   179|---
   180|
   181|## Requirement traceability
   182|
   183|| Issue #2269 requirement | Planned deliverable(s) | Planned test(s) | Acceptance criteria |
   184||---|---|---|---|
   185|| declare target fork/version explicitly | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_verify_script_records_fork_version_via_named_mechanism` | baseline workflow doc declares fork/version; validator records verification mechanism |
   186|| canonical runner command(s) documented | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `examples/openfoam/cavity-v2312/README.md` | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc + manifest provide operator-facing commands |
   187|| minimal smoke case under reproducible repo-tracked path | `examples/openfoam/cavity-v2312/README.md` | `test_manifest_instructions_do_not_commit_case_data` | manifest exists as instruction-only reproducible path |
   188|| validator produces pass/fail output with explicit checks | `scripts/openfoam/verify-openfoam-baseline.sh`, `tests/openfoam/test_verify_openfoam_baseline.py` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_surfaces_runner_failure`, `test_verify_script_normalizes_final_yaml_contract` | validator emits schema-valid pass/fail YAML and preserves root-cause failure behavior |
   189|| common failure modes and version/fork mismatches documented | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `docs/research/openfoam-tutorials.md` | `test_workflow_doc_covers_traceable_issue_requirements` | workflow doc contains troubleshooting + stale path claims normalized |
   190|| workflow executable on canonical engineering host with documented prerequisites | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md`, `scripts/openfoam/verify-openfoam-baseline.sh` | `test_verify_script_succeeds_and_emits_schema_valid_verdict`, `test_verify_script_fails_when_bashrc_missing` | success and failure behavior both pinned for dev-secondary |
   191|
   192|---
   193|
   194|## Risks and Open Questions
   195|
   196|- **Risk:** issue #25 claims broad capability completion in digitalmodel while #2269 is a narrower portability/documentation slice; the implementation must avoid reopening the larger capability scope.
   197|- **Risk:** existing OpenFOAM research/docs disagree on the bootstrap path; implementation must either normalize the sources or document supported-path precedence explicitly.
   198|- **Decision:** mandatory fast smoke tier = `cavity`; optional deeper benchmark tier = `pitzDaily` when operators want stronger convergence confirmation.
   199|- **Decision:** default verdict path = `logs/engineering/openfoam-baseline/latest-verdict.yaml`, with optional caller override via CLI flag for ad hoc runs.
   200|- **Decision:** example manifest remains instruction-only and must not commit copied tutorial case data into git.
   201|
   202|---
   203|
   204|## Complexity: T2
   205|
   206|**T2** — bounded documentation + validation standardization across a small set of repo files, with one existing script to refine and one new deterministic wrapper/example path to add.
   207|
```
