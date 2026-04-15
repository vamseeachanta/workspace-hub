# Adversarial Plan Review Request: Issue #2269

Review the CURRENT plan text only. Be adversarial and concrete. Identify any unresolved blockers, missing retrieval, hidden implementation decisions, non-falsifiable tests/acceptance criteria, governance drift, or approval-readiness gaps.

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
     3|> **Status:** draft
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
    14|- Found: `scripts/openfoam/run-openfoam-tutorials.sh` — existing headless validator already runs `cavity` and `damBreak`, writes a YAML verdict, sources OpenFOAM v2312, and proves there is a real baseline-verification entrypoint to refine rather than invent from scratch.
    15|- Found: `docs/research/openfoam-tutorials.md` — repo research already records that OpenFOAM ESI v2312 is installed on dev-secondary, that `pitzDaily` converged in 281 iterations, and that `cavity`/`damBreak` were later completed headlessly; this provides the strongest existing smoke-case evidence and expected commands/runtime bands.
    16|- Found: `docs/research/openfoam-version-landscape.md` — explicitly recommends the ESI/OpenFOAM.com fork with v2312 syntax for dev-secondary and documents fork-specific dict differences (`turbulenceProperties`, `transportProperties`, `scale`) that the baseline doc must freeze.
    17|- Found: `scripts/pipelines/stubs/stub_openfoam.py` — repo already has a synthetic OpenFOAM stub for higher-level pipeline validation, confirming there is currently no canonical operator-facing baseline workflow doc for real solver execution.
    18|- Gap: no canonical plan artifact exists yet for #2269 under `docs/plans/`, despite the live issue having `status:plan-review`.
    19|- Gap: no repo-tracked OpenFOAM baseline runbook exists under `docs/engineering/portability/`, and no reproducible smoke-case manifest/example path currently exists in the repo.
    20|
    21|### Standards
    22|| Standard | Status | Source |
    23||---|---|---|
    24|| OpenFOAM portability baseline (ESI v2312 on dev-secondary) | done / normative baseline exists | `docs/engineering/portability/PORTABILITY_CONTRACT.md` |
    25|| Engineering artifact portability / machine-role policy | done | `docs/engineering/portability/MACHINE_ROLES.md`, `config/workstations/registry.yaml` |
    26|| External design-code implementation | not applicable for this issue | issue #2269 scope is tool/workflow standardization, not a DNV/API calculation implementation |
    27|
    28|### LLM Wiki pages consulted
    29|- `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` — existing engineering wiki page confirms the capability model: case setup, solver execution, failure diagnosis, validation against tutorial benchmarks, and VTK/ParaView post-processing.
    30|
    31|### Documents consulted
    32|- GitHub issue #2269 — defines the portability baseline goal, required deliverables, and acceptance criteria for standardizing the OpenFOAM workflow.
    33|- GitHub issue #25 — historical OpenFOAM capability issue showing the broader digitalmodel/OpenFOAM capability exists, but documentation remained deferred; #2269 is the bounded portability/documentation/validation follow-on.
    34|- `docs/engineering/portability/PORTABILITY_CONTRACT.md` — locks OpenFOAM (ESI) v2312 on dev-secondary as the canonical CFD baseline and defines which artifacts must become repo-tracked portable knowledge.
    35|- `config/workstations/registry.yaml` — confirms dev-secondary (`ace-linux-2`) is the engineering execution machine with `openfoam`, `paraview`, `gmsh`, and `tmux` installed.
    36|- `data/document-index/online-resource-registry.yaml` — contains both the upstream OpenFOAM core repo entry and the ESI/OpenCFD fork entry, reinforcing that the plan should document which fork/baseline this repo standardizes.
    37|- `docs/document-intelligence/data-intelligence-map.md` and `docs/document-intelligence/README.md` — confirm where engineering registries and intelligence entry points live for future discoverability, so the baseline plan can anchor its sources to the canonical intelligence surfaces.
    38|
    39|### Gaps identified
    40|- No canonical local plan exists for #2269.
    41|- No repo-tracked baseline workflow doc currently states the exact OpenFOAM fork/version, environment bootstrap, runner commands, evidence artifacts, and failure modes for the workspace-hub engineering host.
    42|- No canonical reproducible smoke-case manifest/example path currently exists in the repo for OpenFOAM baseline validation.
    43|- Existing `run-openfoam-tutorials.sh` is useful but not yet framed as the canonical operator-facing baseline validator with explicit prerequisites, output path contract, and failure-mode guidance.
    44|- README/index governance drift exists because the issue carries `status:plan-review` without a canonical local plan artifact or any provider review artifacts.
    45|
    46|<!-- Verification: distinct sources >= 3. Current count: 9 -->
    47|
    48|---
    49|
    50|## Artifact Map
    51|
    52|| Artifact | Path |
    53||---|---|
    54|| This plan | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` |
    55|| Planning index row | `docs/plans/README.md` |
    56|| Canonical baseline workflow doc | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` |
    57|| Baseline validator | `scripts/openfoam/verify-openfoam-baseline.sh` |
    58|| Existing tutorial runner (to refine/reuse) | `scripts/openfoam/run-openfoam-tutorials.sh` |
    59|| Smoke-case manifest/example | `examples/openfoam/cavity-v2312/README.md` |
    60|| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2269-claude.md` |
    61|| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2269-codex.md` |
    62|| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2269-gemini.md` |
    63|
    64|---
    65|
    66|## Deliverable
    67|
    68|A repo-tracked OpenFOAM baseline package for dev-secondary that freezes ESI v2312 as the canonical fork/version, documents the exact workflow and failure modes, provides a reproducible smoke-case manifest, and exposes a deterministic validator that emits explicit pass/fail evidence.
    69|
    70|---
    71|
    72|## Pseudocode
    73|
    74|```text
    75|inspect existing OpenFOAM research notes, tutorial runner, and portability contract
    76|lock the canonical baseline:
    77|    machine = dev-secondary
    78|    fork = ESI / OpenFOAM.com
    79|    version = v2312
    80|    environment source path = detected canonical bashrc path
    81|write a baseline workflow doc that records:
    82|    supported fork/version
    83|    environment bootstrap command
    84|    canonical tutorial-based smoke cases
    85|    output evidence contract
    86|    common failure modes and troubleshooting guidance
    87|create a baseline validator wrapper that:
    88|    verifies OpenFOAM bashrc exists
    89|    records resolved version/fork information
    90|    invokes the existing tutorial runner or equivalent checks
    91|    writes a deterministic verdict artifact to a repo-documented path
    92|create a repo-tracked smoke-case manifest/example path for cavity-v2312
    93|verify the validator reports PASS on the expected happy path and FAIL with actionable messaging when prerequisites are missing
    94|```
    95|
    96|---
    97|
    98|## Files to Change
    99|
   100|| Action | Path | Reason |
   101||---|---|---|
   102|| Create | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` | canonical local plan artifact |
   103|| Update | `docs/plans/README.md` | add canonical plan index row and correct local state to `draft` |
   104|| Create | `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` | canonical operator-facing baseline workflow doc |
   105|| Create | `scripts/openfoam/verify-openfoam-baseline.sh` | deterministic validation entrypoint with explicit pass/fail evidence |
   106|| Update | `scripts/openfoam/run-openfoam-tutorials.sh` | reuse/tighten existing tutorial runner as the underlying smoke validation engine |
   107|| Create | `examples/openfoam/cavity-v2312/README.md` | repo-tracked smoke-case manifest/example path |
   108|
   109|---
   110|
   111|## TDD Test List
   112|
   113|| Test name | What it verifies | Expected input | Expected output |
   114||---|---|---|---|
   115|| `test_baseline_doc_locks_esi_v2312` | baseline doc names the canonical fork/version and execution machine explicitly | baseline doc text | ESI/OpenFOAM.com v2312 on dev-secondary |
   116|| `test_verify_script_fails_when_bashrc_missing` | validator fails fast with actionable error when OpenFOAM is unavailable | missing or invalid bashrc path | non-zero exit + explicit missing-bashrc message |
   117|| `test_verify_script_emits_deterministic_verdict_yaml` | validator writes a documented verdict artifact with machine/version/tutorial status | runnable environment | YAML verdict with overall verdict + per-check results |
   118|| `test_tutorial_runner_contract_is_reused` | validator delegates to the existing tutorial runner instead of re-implementing tutorial orchestration from scratch | validator invocation | calls or wraps `run-openfoam-tutorials.sh` |
   119|| `test_smoke_case_manifest_exists` | repo contains a stable smoke-case example path for operators | repo tree | `examples/openfoam/cavity-v2312/README.md` present with commands + expected outputs |
   120|| `test_failure_modes_are_documented` | baseline doc enumerates common version/fork mismatch and missing-tool failures | baseline doc text | troubleshooting section with explicit failure cases |
   121|
   122|---
   123|
   124|## Acceptance Criteria
   125|
   126|- [ ] Canonical plan file exists locally for #2269 and `docs/plans/README.md` reflects local status `draft` until adversarial review artifacts exist.
   127|- [ ] `docs/engineering/portability/openfoam-v2312-baseline-workflow.md` explicitly declares the canonical fork/version, machine, bootstrap command, smoke cases, and troubleshooting guidance.
   128|- [ ] `scripts/openfoam/verify-openfoam-baseline.sh` emits deterministic pass/fail evidence rather than relying on ad hoc shell history.
   129|- [ ] A repo-tracked smoke-case manifest/example path exists for the v2312 cavity baseline.
   130|- [ ] The validator contract reuses or tightens the existing tutorial runner instead of creating a second overlapping validation path.
   131|- [ ] Common failure modes (missing bashrc, wrong fork/version assumptions, tutorial lookup failure) are documented with explicit operator guidance.
   132|
   133|---
   134|
   135|## Adversarial Review Summary
   136|
   137|| Provider | Verdict | Key findings |
   138||---|---|---|
   139|| Claude | PENDING | draft not yet reviewed |
   140|| Codex | PENDING | draft not yet reviewed |
   141|| Gemini | PENDING | draft not yet reviewed |
   142|
   143|**Overall result:** PENDING — draft must complete adversarial review before the issue can honestly remain in `status:plan-review`.
   144|
   145|Revisions made based on review:
   146|- none yet — initial canonical draft created to resolve the missing-plan gap.
   147|
   148|---
   149|
   150|## Risks and Open Questions
   151|
   152|- **Risk:** existing OpenFOAM research notes reference both `/opt/openfoam2312/etc/bashrc` and `/usr/lib/openfoam/openfoam2312/etc/bashrc`; the implementation must resolve and document the actual supported bootstrap path(s) without hand-waving.
   153|- **Risk:** issue #25 claims broad capability completion in digitalmodel while #2269 is a narrower portability/documentation slice; the plan must avoid reopening the larger capability scope.
   154|- **Open:** should the smoke-case manifest remain purely tutorial-based (`cavity`) for fast validation, or should the baseline include `pitzDaily` as a second optional case because it already has the strongest historical convergence evidence?
   155|- **Open:** should the validator write only to an operator-supplied output path, or should the workflow also standardize a default artifact directory under `logs/engineering/`?
   156|
   157|---
   158|
   159|## Complexity: T2
   160|
   161|**T2** — bounded documentation + validation standardization across a small set of repo files, with one existing script to refine and one new deterministic wrapper/example path to add.
   162|
```
