# Plan for [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427): Repository-Linked Algorithm Run Datasets

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3427
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-10-plan-3427-claude.md` | `scripts/review/results/2026-07-10-plan-3427-codex.md` | `scripts/review/results/2026-07-10-plan-3427-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `docs/architecture/execution-manifest.schema.yaml` defines commands, replay and
  regeneration instructions, environment pins, checksums, tests, legal evidence,
  promotion gates, and report eligibility. It does not define a composite algorithm
  version, canonical public input set, output equality set, or Hugging Face revision.
- `docs/architecture/report-evidence-bundle.schema.yaml` defines audience, derivation,
  source bindings, published claims, legal evidence, and review state. It does not
  define the standard rolling algorithm report, mandatory Inputs/Outputs sections, or
  run/metric revision bindings.
- `docs/registry/workflow-manifest.json` at workspace-hub
  `origin/main@0a08c27aaaf1` supplies `repo:id@version` workflow discovery,
  registry hashes, invocation metadata, and structured descriptor slots. Its live
  `--check` currently fails for every registered repository, so future publication will
  consume it only after a freshness check passes.
- `assetutilities/src/assetutilities/workflow_api/envelope.py` at
  `origin/main@82888f1b6e09` supplies the shared
  `ResultEnvelope`, code-version evidence, input/result hashes, confidence, warnings,
  and measured reproducibility. Its input hash intentionally removes volatile top-level
  configuration and its code version does not prove a clean tree; the public ledger will
  retain these values as execution evidence rather than reuse them as strict identity.
- `worldenergydata/src/worldenergydata/workflow_api/runner.py` at
  `origin/main@0c5393b18590` consumes the shared
  envelope and normalizes container hashes, but its current provenance timestamp is a
  run timestamp rather than a pinned source-data snapshot. The public input contract
  will require the latter.
- `digitalmodel/docs/registry/workflows.yaml` and
  `src/digitalmodel/workflow_api/{runner,provenance,golden}.py` at
  `origin/main@529c4ba13d90` define versioned workflow routing, a repository runner,
  provenance adaptation, a golden harness, and four workflow goldens. The public ledger
  will crosswalk each surface rather than create a competing runner. The sample result
  manifest at the same ref still uses a label-like run ID, a Git SHA, and a machine-local
  source path rather than a strict public run ID.
- `worldenergydata/data/source-refresh-acceptance-contract.json` at
  `origin/main@0c5393b18590` defines source
  authority, public URL, freshness, completeness, and refresh evidence. Existing BSEE
  product manifests carry file hashes and review gates but no complete algorithm
  version, canonical input snapshot, or environment identity.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue lifecycle and user approval | binding | `AGENTS.md`, `docs/plans/README.md` |
| Data/execution/report boundaries | reusable, extension required | `docs/architecture/execution-manifest.schema.yaml`, `docs/architecture/report-evidence-bundle.schema.yaml` |
| Durable architecture ownership | binding | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` |
| Control-plane discovery | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Legal/public-egress scan | binding | `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml` |
| Hugging Face dataset repository history and formats | applicable external platform contract | <https://huggingface.co/docs/hub/datasets-adding> |
| Hugging Face dataset card metadata | applicable external platform contract | <https://huggingface.co/docs/hub/datasets-cards> |
| Hugging Face commit and preupload behavior | applicable external platform contract | <https://huggingface.co/docs/huggingface_hub/guides/upload> |

No engineering calculation standard applies to this governance issue. Child algorithm
plans will retain their existing calculation citation obligations.

### LLM Wiki pages consulted

- No domain wiki page governs this run-data contract. The durable/transient boundary
  assigns approved normative architecture to durable repository documentation, while
  GitHub issues, plans, and review artifacts remain execution-state evidence.
- `docs/document-intelligence/README.md` and
  `docs/document-intelligence/data-intelligence-map.md` identify the current registry
  and intelligence entry points; neither contains an algorithm-run ledger.

### Documents consulted

- Parent [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) fixes the
  repository-specific dataset, replay, identity, reporting, metrics, and staged-promotion
  decisions and explicitly authorizes planning only.
- Closed architecture [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726)
  and its execution/report schemas establish the data-to-report boundaries this plan
  will extend rather than replace.
- Plan-approved [#3282](https://github.com/vamseeachanta/workspace-hub/issues/3282),
  [#3283](https://github.com/vamseeachanta/workspace-hub/issues/3283), and
  [#3284](https://github.com/vamseeachanta/workspace-hub/issues/3284) define the
  execution envelope, determinism harness, and workflow discovery manifest. The parent
  contract will add an explicit compatibility crosswalk and stricter public identity.
- Plan-approved [#3285](https://github.com/vamseeachanta/workspace-hub/issues/3285)
  owns digitalmodel adoption. Fetched `digitalmodel origin/main@529c4ba13d90`
  contains its runner, provenance adapter, golden harness, and four golden fixtures even
  though the issue remains open; the public contract will consume that live substrate.
- Open [#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975) and
  [#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) own related
  provenance/routing and public-egress controls. Publication will consume their controls
  without making them the algorithm-run schema owner.
- Closed [digitalmodel #656](https://github.com/vamseeachanta/digitalmodel/issues/656)
  demonstrates a results store with a per-run manifest, while open
  [worldenergydata #453](https://github.com/vamseeachanta/worldenergydata/issues/453)
  demonstrates provenance-gated insight publication. Neither provides the complete
  cross-repository contract requested here.
- The drive-index query at `2026-07-10T08:07:20Z` searches six registered indexes. Five
  respond; one stale worktree-local index is unreachable. Eight low-score, single-token
  CAD/restricted-path matches are irrelevant and remain unopened. No relevant drive file
  informs this public architecture.
- Hugging Face documents Parquet as the recommended general dataset format, JSONL as a
  nested-data alternative, Git-backed revision history, dataset-card metadata, and
  preupload plus single-commit support for large files. The architecture will use those
  capabilities but will add repository-side validation and cross-system acceptance.

### Gaps identified

- No machine-readable decision contract ties the locked decisions, record categories,
  repository ownership, state machine, failure rules, and issue dependency graph together.
- No explicit crosswalk separates execution-envelope hashes from strict public identity.
- No crosswalk enumerates the landed digitalmodel runner, provenance adapter, golden
  harness, and golden fixtures as execution evidence inputs to the public ledger.
- No explicit mapping distinguishes the existing integer workflow registry version from
  the required semantic algorithm version; inferring one from the other would be unsafe.
- No shared contract states that cross-system atomicity applies to acceptance rather than
  visibility, or defines recovery when the HF commit succeeds but report pinning fails.
- No standard defines the mandatory/optional rolling HTML report sections and exact
  revision-pin rule across both source repositories.
- No public run-ledger validation test guards against weakening replay completeness,
  clean-source requirements, failure exclusions, per-repository residency, or child gates.

### Evidence (embedded verification)

**Issue statuses** (verified `2026-07-10T08:11:16Z` via `gh issue view`):

| Issue | State | Planning state / relationship |
|---|---|---|
| [#3427](https://github.com/vamseeachanta/workspace-hub/issues/3427) | OPEN | `status:needs-plan`, parent |
| [#3428](https://github.com/vamseeachanta/workspace-hub/issues/3428) through [#3432](https://github.com/vamseeachanta/workspace-hub/issues/3432) | OPEN | `status:needs-plan`, shared contract children |
| [#3433](https://github.com/vamseeachanta/workspace-hub/issues/3433) | OPEN | `status:needs-plan`, publication child |
| [digitalmodel #1505](https://github.com/vamseeachanta/digitalmodel/issues/1505) | OPEN | `status:needs-plan`, public synthetic pilot |
| [worldenergydata #927](https://github.com/vamseeachanta/worldenergydata/issues/927) | OPEN | `status:needs-plan`, public BSEE pilot |
| [#3434](https://github.com/vamseeachanta/workspace-hub/issues/3434) | OPEN | `status:needs-plan`, insights child |
| [#3282](https://github.com/vamseeachanta/workspace-hub/issues/3282), [#3283](https://github.com/vamseeachanta/workspace-hub/issues/3283), [#3284](https://github.com/vamseeachanta/workspace-hub/issues/3284), [#3285](https://github.com/vamseeachanta/workspace-hub/issues/3285) | OPEN | `status:plan-approved`; substantial envelope, manifest, digitalmodel runner/provenance/golden, and worldenergydata runner artifacts are on remote main while issue closure remains pending |
| [#2975](https://github.com/vamseeachanta/workspace-hub/issues/2975), [#3013](https://github.com/vamseeachanta/workspace-hub/issues/3013) | OPEN | related provenance/public-egress work |

**File existence** (fetched remote refs verified `2026-07-10T08:42:11Z`):

```text
EXISTS docs/architecture/execution-manifest.schema.yaml
EXISTS docs/architecture/report-evidence-bundle.schema.yaml
EXISTS docs/registry/workflow-manifest.json
EXISTS docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html (draft)
EXISTS assetutilities origin/main@82888f1b6e09:src/assetutilities/workflow_api/envelope.py
EXISTS worldenergydata origin/main@0c5393b18590:src/worldenergydata/workflow_api/runner.py
EXISTS digitalmodel origin/main@529c4ba13d90:src/digitalmodel/workflow_api/runner.py
EXISTS digitalmodel origin/main@529c4ba13d90:src/digitalmodel/workflow_api/provenance.py
EXISTS digitalmodel origin/main@529c4ba13d90:src/digitalmodel/workflow_api/golden.py
EXISTS digitalmodel origin/main@529c4ba13d90:tests/workflow_api/goldens/{4 fixtures}
MISSING docs/architecture/algorithm-run-dataset-contract.yaml (planned)
MISSING tests/architecture/test_algorithm_run_dataset_contract.py (planned)
```

**Current drift and contract excerpts:**

```text
$ uv run --no-project --with pyyaml scripts/workflow/generate_workflow_manifest.py --check
STALE: registries changed since manifest: [all four registered repositories]

digitalmodel pyproject package version: 0.1.1
digitalmodel runtime __version__:       0.0.9
sample result run_id:                   baseline
sample result source path:              machine-local absolute path

ResultEnvelope code_version:            {package_version, git_sha}
ResultEnvelope reproducible default:     null unless measured
worldenergydata provenance data_as_of:   runtime UTC timestamp
```

**Reproduction proofs:** N/A. This parent concerns architecture/governance and does not
allege a runtime regression. The stale-manifest check above is a read-only compatibility
probe, not the issue premise.

Distinct sources: parent issue; two existing architecture schemas; workflow manifest and
generator; ResultEnvelope implementation; two source repositories; four related issue
families; document-intelligence maps; drive-index probe; three official Hugging Face pages
(more than the required three sources).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-10-issue-3427-repository-linked-algorithm-run-datasets.md` |
| Decision manual draft / future normative view | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` |
| Machine-readable decision contract | `docs/architecture/algorithm-run-dataset-contract.yaml` |
| Contract tests | `tests/architecture/test_algorithm_run_dataset_contract.py` |
| Documentation entry point | `docs/README.md` |
| Plan review - Claude | `scripts/review/results/2026-07-10-plan-3427-claude.md` |
| Plan review - Codex | `scripts/review/results/2026-07-10-plan-3427-codex.md` |
| Plan review - Gemini | `scripts/review/results/2026-07-10-plan-3427-gemini.md` |

---

## Deliverable

A machine-validated parent architecture contract and human-readable HTML decision manual
will define repository-specific public run datasets, strict identity and replay boundaries,
record ownership, promotion/acceptance states, report rules, compatibility with the existing
workflow envelope, and the independently gated child issue graph.

The committed HTML file is an ungated design companion whose complete contents will
remain in plan-review scope. It will become normative only after this plan receives user
approval and the future YAML contract plus parity tests land through TDD.

---

## Pseudocode

```text
load contract YAML
require schema version, decision list, owners, records, states, exclusions, and issue graph
assert one dataset target per source repository and no combined domain-run dataset
assert algorithm version requires semantic version, clean commit, schema versions, environment digest
assert run identity requires canonical input set, explicit seed, and execution parameters
assert run identity excludes outputs; exact replay compares a versioned output equality digest
assert input binding IDs are independent of run IDs and publication state is append-only
assert public input policy rejects restricted, pointer-only, unlicensed, unhashed, or incomplete inputs
assert failed runs cannot contribute metric observations, insights, or decisions
assert report contract always includes Inputs and Outputs and pins an exact HF revision
assert publication graph reaches accepted only through validation, replay, review, HF commit,
       report pin, and cross-system verification
assert ResultEnvelope and workflow-manifest fields are evidence inputs, not strict identity aliases
assert digitalmodel runner, provenance, golden harness, and golden fixtures have crosswalk entries
assert every child issue has an exact URL, owner repository, dependency, and independent approval gate
parse HTML with Python stdlib html.parser; load YAML with the existing PyYAML dependency
verify manual sections, decisions, issue links, and contract version agree with YAML
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/algorithm-run-dataset-contract.yaml` | machine-readable source for decisions, ownership, records, states, compatibility, and issue DAG |
| Update | `docs/governance/2026-07-10-algorithm-run-dataset-decision-manual.html` | incorporate review changes and bind the human view to the contract version |
| Create | `tests/architecture/test_algorithm_run_dataset_contract.py` | TDD guard using stdlib `html.parser` plus existing PyYAML; no dependency change |
| Update | `docs/README.md` | expose the approved durable architecture from the documentation entry point |
| Update | `docs/plans/README.md` | keep the plan index status and review summary current |

The parent implementation will not modify source code, workflow registries, source-repository
reports, Hugging Face datasets, credentials, or any child issue's implementation paths.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_contract_has_locked_decisions_and_records` | every approved decision and record category is explicit | contract YAML | complete required sets |
| `test_dataset_ownership_is_per_repository` | dedicated dataset mapping and catalog-only aggregation | repository map | two distinct targets, no combined run table |
| `test_algorithm_and_run_identity_fail_closed` | clean commit/version/schema/environment/input/seed requirements | invalid and valid identity fixtures | invalid rejected; valid accepted |
| `test_output_equality_policy_is_versioned` | raw byte default and explicit semantic canonicalizer exception | output policies | ambiguous normalization rejected |
| `test_public_input_admission_is_strict` | restricted, pointer-only, missing-license, unpinned, or unhashed inputs fail | input policy cases | each unsafe case rejected |
| `test_failed_runs_are_analysis_ineligible` | failures remain visible but cannot feed metrics/insights/decisions | status eligibility map | failure edges absent |
| `test_promotion_state_machine_has_no_gate_bypass` | accepted state requires every gate and defines candidate recovery | transition graph | no shortcut path |
| `test_report_contract_has_mandatory_sections_and_exact_revision` | Inputs/Outputs always render and moving references fail | report contract | mandatory sections and immutable pin |
| `test_result_envelope_crosswalk_does_not_alias_identity` | envelope plus digitalmodel runner/provenance/golden surfaces remain evidence only | compatibility map | all landed surfaces mapped; no identity alias to input/result hashes |
| `test_issue_graph_is_complete_acyclic_and_independently_gated` | all nine children, exact URLs, dependencies, own approval | issue graph | complete DAG, no parent authorization inheritance |
| `test_html_manual_matches_contract` | manual anchors, decisions, records, states, links, and version match YAML | YAML plus HTML | parity passes |
| `test_legal_scan_passes` | no restricted identifiers, secrets, or machine paths enter artifacts | changed paths | scanner exit 0 |

---

## Acceptance Criteria

- [ ] Tests will be written first and will fail before the contract implementation exists.
- [ ] `docs/architecture/algorithm-run-dataset-contract.yaml` will encode every locked
      decision, record category, owner, state transition, rejection reason, compatibility
      boundary, and exact child issue URL.
- [ ] The contract will distinguish byte identity from a versioned semantic equality
      digest and will fail closed when an output canonicalizer is undeclared.
- [ ] The contract will distinguish atomic acceptance from cross-system visibility and
      will define an append-only Publication record plus recovery for an HF candidate
      commit without a verified report pin; Run records will not mutate on acceptance.
- [ ] The existing `ResultEnvelope`, determinism harness, and workflow manifest will map
      into execution evidence without becoming aliases for strict public run identity.
- [ ] The compatibility crosswalk will enumerate the landed digitalmodel runner,
      provenance adapter, golden harness, and four golden fixtures at a fetched remote ref.
- [ ] Integer workflow registry versions will remain execution references and will map
      explicitly, never implicitly, to semantic algorithm versions.
- [ ] The HTML manual will contain mandatory Inputs/Outputs reporting rules, optional
      section activation, dataset layout, JSON examples, issue ownership, and exact
      Hugging Face/source-repository revision rules.
- [ ] The issue DAG will contain all nine child issues, keep each child at its own approval
      gate, and state that parent approval cannot authorize child implementation.
- [ ] `uv run pytest tests/architecture/test_algorithm_run_dataset_contract.py -v` will pass.
- [ ] `scripts/enforcement/check-no-abs-paths.sh` will pass on the changed files.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` will pass after intent-to-add staging
      exposes new files to the scanner.
- [ ] The HTML will parse without errors and will pass desktop/mobile visual inspection.
- [ ] HTML/YAML parity tests will use Python stdlib `html.parser` and the repository's
      existing PyYAML dependency; this parent will add no package or lockfile dependency.
- [ ] Claude, Codex, and Gemini review artifacts will be non-empty or will record an
      explicit provider outage; no unresolved MAJOR finding will remain.
- [ ] No source-repository algorithm code, report, dataset, or HF resource will change
      under this parent issue.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | adversarial plan review will run after the exact plan commit is pushed |
| Codex | PENDING | adversarial plan review will run after the exact plan commit is pushed |
| Gemini | PENDING | adversarial plan review will run after the exact plan commit is pushed |

**Overall result:** PENDING

Review revisions will be recorded here after the T3 wave.

---

## Risks and Open Questions

- **Cross-system transaction risk:** GitHub and Hugging Face cannot commit atomically.
  The contract will make candidate visibility non-authoritative and will gate acceptance
  on verified HF records plus a pinned source-repository report.
- **Existing-envelope drift:** mutable local feature checkouts lag fetched remote main,
  while the committed discovery manifest is stale. Implementation will fetch and pin
  sibling refs, re-run discovery, and fail closed instead of trusting local branches,
  labels, or old snapshots.
- **Canonicalization risk:** removing volatile fields can remove real inputs, while raw
  office/archive bytes can contain irrelevant timestamps. Child contracts will require
  algorithm-owned input schemas and versioned semantic canonicalizers with raw hashes.
- **License risk:** a repository-level dataset license cannot grant rights absent from an
  input source. Public admission will require per-input rights evidence and legal review.
- **Scale risk:** many small files degrade repository usability. The publisher child will
  tune append-only Parquet shard and content-object thresholds against current HF limits.
- **Namespace/auth risk:** the final HF organization and credentials are not verified by
  this planning issue. The publisher child will perform an authenticated ownership
  preflight without writing secrets to repositories or logs.

No parent-level design question remains open. Canonical serialization, environment
vocabulary, output canonicalizers, shard thresholds, and authenticated namespace are
owned by the named children and cannot weaken the parent invariants.

---

## Complexity: T3

**T3** - this is a systemic, cross-repository data/publication architecture with legal,
identity, determinism, reporting, external-platform, and child-governance consequences.
It requires a three-provider adversarial plan review even though the parent implementation
will remain documentation and contract-test scoped.
