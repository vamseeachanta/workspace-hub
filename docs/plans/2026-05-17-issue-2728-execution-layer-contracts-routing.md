# Plan for #2728: Define execution layer contracts, tooling, and compute routing

> **Status:** `status:plan-approved` — user approved on 2026-05-18; implementation authorized
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2728
> **Review artifacts:** prior-cycle blockers are summarized in `scripts/review/results/2026-05-17-plan-2728-disagreement.md`; current-cycle Claude/Codex/Gemini artifacts must be generated after this revision and verified non-empty before an approval request. Do not cite same-cycle per-provider paths from this plan body.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/DATA_RESIDENCE_POLICY.md` — existing three-tier data model separates collection data (`worldenergydata`), engineering reference data (`digitalmodel`), and project/client data (`client_projects` / equivalent), with path-based handoff conventions and git/LFS/external-storage thresholds.
- Found: `data/document-index/mounted-source-registry.yaml` — existing mounted-source registry already enumerates local, remote, API, standards, literature, and project-document source roots, including `/mnt/local-analysis/workspace-hub`, `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/docs`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/ace/docs/literature/dde (migrated local copy; remote DDE archival)`, and `api://worldenergydata`.
- Found: `docs/content-pipeline/README.md` — existing source → transform → stage → review → publish pipeline for turning internal wiki/source material into public/client-facing website content.
- Found: `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — current repo ecosystem summary names workspace-hub as control plane, documented core engineering/data repos, skills, scripts, document-intelligence, llm-wiki, and report/docs locations; only explicitly documented repos may be called tier-1.
- Gap: No single current architecture contract defines the data → execution → report layer boundaries across `/mnt` data, client project data, documented tiered repo data, public/private `llm-wiki`, execution machines, and report/chatbot surfaces.

### Standards
| Standard | Status | Source |
|---|---|---|
| Repo workflow hard gates | applicable | `AGENTS.md`; `docs/plans/README.md` |
| Data residence | applicable but needs expansion | `docs/DATA_RESIDENCE_POLICY.md` |
| Legal/security scan | applicable | `scripts/legal/legal-sanity-scan.sh` |

### LLM Wiki pages consulted
- Public/private `llm-wiki` location must be inventoried from tracked repo maps and live filesystem evidence; this plan must not assume a sibling clone or nested path is authoritative without embedded command output.
- `docs/content-pipeline/README.md` lists existing internal wiki sources and publication transform rules that strip internal references before public publication.

### Documents consulted
- [#2728](https://github.com/vamseeachanta/workspace-hub/issues/2728) — issue body requests this architecture review and layer-specific scope.
- [#2119](https://github.com/vamseeachanta/workspace-hub/issues/2119) — overlapping machine dispatch/workload routing contract; #2728 must cross-link or defer machine policy instead of duplicating it.
- [#1838](https://github.com/vamseeachanta/workspace-hub/issues/1838) and [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089) — overlapping provider/session and AI-routing governance.
- [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) and [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) — overlapping data/repo location inventory and mount taxonomy; #2728 consumes their source IDs/path contract, not redefines them.
- [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726) — parent architecture issue for data, execution, and report layer boundaries.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — control-plane boundary for harness/infrastructure work.
- `config/agents/` and `.claude/rules/` — agent/runtime governance references required for harness/infrastructure plans.
- `docs/DATA_RESIDENCE_POLICY.md` — current data residence policy and examples.
- `data/document-index/mounted-source-registry.yaml` — known mounted/API source roots.
- `docs/content-pipeline/README.md` — current internal knowledge to public website pipeline.
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — current ecosystem inventory summary.

- `docs/BUSINESS_BRAIN.md` — existing knowledge-promotion authority; architecture docs must reference this instead of creating a competing promotion policy.
- `docs/document-intelligence/README.md` — universal document-intelligence retrieval entry point.
- `docs/document-intelligence/data-intelligence-map.md` — source/corpus intelligence map for data/report routing.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — existing durable vs transient promotion boundary; report-derived learnings must reconcile with it.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — existing intelligence-layer terminology; this plan's layer codes are architecture-surface codes, not replacements for document-intelligence L1/L2/L3/L5.
- `data/document-index/registry.yaml` — current document-index registry source of truth.
- `data/document-index/resource-intelligence-maturity.yaml` — current resource-intelligence maturity model.

### Initial known data/source classes to include in the architecture
| Source class | Initial known examples / roots | Initial disposition |
|---|---|---|
| `/mnt` workspace/control-plane data | `/mnt/local-analysis/workspace-hub`; sibling repo checkouts under `/mnt/local-analysis/`; worktrees under `/mnt/local-analysis/worktrees/` | Repo/control-plane evidence; inventory without assuming all paths are canonical |
| Repo-ecosystem data | `workspace-hub` control-plane data; documented tier-1 engineering/data repos such as `digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`; knowledge/publication/strategy repos such as `llm-wiki`, `aceengineer-website`, `aceengineer-strategy` only where tracked registry evidence supports that role | Repo-backed data/config/docs; classify by owner repo, documented tier, and public/private posture; do not infer tier-1 status from local checkout name |
| Public collection data | `worldenergydata` APIs/sources: BSEE, SODIR, NDBC, MarineTraffic, marine safety incidents, oil prices, LNG terminals | D-L1/D-L2 data-layer candidates; raw not committed unless policy allows |
| Engineering reference data | `digitalmodel` reference tables; standards-derived constants; SN curves; steel grades; hydrodynamic coefficients | Data-layer curated/reference; must carry provenance/license/citation sidecars where applicable |
| Mounted standards/literature | `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/acma-codes`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/ace/docs/literature/dde (migrated local copy; remote DDE archival)` | Reference-in-place; never blindly copy into public repos |
| Client/project data | `client_projects` / project repos / mounted project archives / local client folders | Private by default; sanitized derivatives only |
| `llm-wiki` raw-like data | source inventories, extracted notes, staging packs, source cards, provenance metadata, RAG indexes | Private/local or controlled staging until reviewed |
| Public `llm-wiki` content | sanitized markdown pages and public chatbot/search corpus | Public-facing after source/legal/sanitization gates |
| Execution artifacts | issue plans, YAML/JSON configs, prompt bundles, tool manifests, run logs, checksums | Execution/report boundary; promote only manifests/evidence, not bulky generated data by default |
| Report artifacts | internal reports, client HTML, limited PDFs, chatbot/query configs/indexes | Report layer; audience-specific evidence and sanitization gates required |

### Gaps identified
- No approved level taxonomy yet for D-L1 raw → D-L2 raw-like/private staging → D-L3 curated knowledge → D-L4 indexes/query surfaces.
- No approved level taxonomy yet for execution inputs vs data-layer inputs, code/tooling, machines/compute, validation evidence, and handoff manifests.
- No approved level taxonomy yet for report raw outputs, data outputs, HTML/PDF/report formats, interactivity, and chatbot surfaces.
- No canonical matrix yet mapping source class → owner repo/path → public/private posture → promotion gate → report/chatbot eligibility.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-17T01:12:21Z via `gh issue view`):
- `#2728` — OPEN — feat(architecture): define execution layer contracts, tooling, and compute routing
- `#2726` — OPEN — feat(architecture): review data, execution, and report layer boundaries

**File existence / evidence sources**:
- EXISTS: `docs/DATA_RESIDENCE_POLICY.md`
- EXISTS: `data/document-index/mounted-source-registry.yaml`
- EXISTS: `docs/content-pipeline/README.md`
- EXISTS: `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`

**Line excerpts consulted**:
```text
docs/DATA_RESIDENCE_POLICY.md:13-15 — Tier 1 Collection Data = `worldenergydata`; Tier 2 Engineering Reference Data = `digitalmodel`; Tier 3 Project Data = project repos/client_projects.
docs/DATA_RESIDENCE_POLICY.md:62 — project-specific configurations, analysis inputs/outputs, and client deliverables are never stored in `worldenergydata` or `digitalmodel`.
data/document-index/mounted-source-registry.yaml:5-48,163-183 — tracked source roots include `workspace_hub_local`, standards/literature mounts, project/docs mounts, API metadata virtual root, and ACMA codes local root.
docs/content-pipeline/README.md:3,27,51-58,99 — internal knowledge is transformed into client-facing content by stripping internal references/metadata and targeting zero internal references in output.
docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md:106-113 — documented Tier-1 core engineering repos are `digitalmodel`, `assetutilities`, `assethold`, and `worldenergydata`; other local repos require separate role classification.
config/workstations/registry.yaml:3 — all machine identity/capability data lives in this registry; execution routing docs must reference it instead of duplicating machine truth.
docs/BUSINESS_BRAIN.md:106-115 — knowledge promotion requires explicit source/provenance/license/legal gates and `git add -N <new-files> && scripts/legal/legal-sanity-scan.sh --diff-only` for reviewed diffs.
docs/document-intelligence/README.md:1-80; docs/document-intelligence/durable-vs-transient-knowledge-boundary.md:1-120 — durable public/private knowledge boundaries must govern report-derived learning promotion.
data/document-index/registry.yaml and resource-intelligence-maturity.yaml — document-index/resource-intelligence sources must be read before final implementation; architecture contracts should link rather than fork these registries.
```

**Gap proofs**:
- Initial drafting search found no existing plan files for 2726-2729; revised plan now treats existing `scripts/review/results/2026-05-17-plan-272[6-9]-*.md` MAJOR artifacts as active blockers to clear before approval.
- Existing policies cover important pieces but not the full cross-layer architecture and level taxonomy requested here.

**Reproduction proofs**:
N/A — architecture/governance planning issue, not a runtime failure.

<!-- Distinct sources: issue body, parent issue, DATA_RESIDENCE_POLICY, mounted-source-registry, content-pipeline README, capabilities summary, related open issues, review artifacts. -->


---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-17-issue-2728-execution-layer-contracts-routing.md` |
| Execution layer contract | `docs/architecture/execution-layer-contract.md` |
| Execution input/output manifest schema | `docs/architecture/execution-manifest-schema.md` and `docs/architecture/execution-manifest.schema.yaml` |
| Machine/tool routing policy view | `docs/architecture/execution-routing-policy-view.md` |
| Tests | `tests/architecture/test_execution_layer_contract.py`; fixtures in `tests/fixtures/architecture/execution_manifest.yaml` and `tests/fixtures/architecture/execution_routing_cases.yaml` |
| Execution entry-point inventory | `docs/architecture/execution-entry-point-inventory.md` |
| Execution follow-up issue bundle | `docs/architecture/execution-follow-up-issue-backlog.md` |
| Prior-cycle review synthesis | `scripts/review/results/2026-05-17-plan-2728-disagreement.md` |

---

## Deliverable
An execution-layer contract will define how input data contracts, code/tools, agents, machines/compute, validation, and evidence manifests transform data-layer sources into report-layer eligible artifacts without bypassing gates. It will consume canonical machine capability data from `config/workstations/registry.yaml` and overlapping routing issues (#2119/#1838/#2089), and execution manifests must carry both `input_residency` and `output_residency` so report-layer and data-layer handoffs can be enforced.

This child issue is separately dispatchable only because it owns execution contracts; it must not redefine data-source residency (#2727) or report publication eligibility (#2729). Cross-layer fields (`source_id`, `input_residency`, `output_residency`, evidence bundle links) are interface references to the parent #2726 contract.

---

## Proposed Execution Layer Levels
| Level | Working name | Contents | Boundary rule |
|---|---|---|---|
| E-L1 | Input contracts | YAML/JSON specs, issue plans, source manifests, fixture manifests, prompt bundles | References data sources by source_id/path; does not own raw data |
| E-L2 | Tools/code execution | ingestion scripts, parsers, report generators, validation harnesses, legal scanners, skills/prompts | Code is repo-backed; Python via `uv run`; outputs manifest evidence |
| E-L3 | Compute/runtime placement | registry keys (`dev-primary`, `dev-secondary`, `licensed-win-1`, `licensed-win-2`, etc.), hostnames as attributes only, local worktrees, background jobs, and provider tools as machine capabilities | Routing contract references `config/workstations/registry.yaml` as canonical machine registry; docs may derive views but cannot duplicate source-of-truth fields |
| E-L4 | Validation/evidence | tests, legal scan outputs, adversarial review artifacts, checksums, run manifests, command logs | Required handoff to report layer; raw logs remain internal unless sanitized |

---

## Pseudocode
```text
function validate_execution_contract(execution_manifest):
    validate manifest schema, declared data source_ids, input_residency, and output_residency
    verify source availability and permission posture through the data-layer `source_id` plus `source_registry_kind` contract; use `mounted-source-registry.yaml` only for mounted-source rows, repo/document-index rows through their registry refs, and fail closed on repo/client/wiki paths not represented by #2727 or explicitly blocked on #2731/#2732
    route work to capable machine/tool using config/workstations/registry.yaml; treat #2119/#1838/#2089 as open dependencies, not approved policy
    document the repo-backed run command/regeneration_command, isolated workdir/worktree, tests, legal scan, checksums, output manifest, and review artifacts
    mark outputs report-eligible only if validation/evidence gates and output_residency allow it; runtime orchestrator enforcement is deferred to filed follow-up issue unless explicitly implemented
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/execution-layer-contract.md` | Defines execution levels and layer boundaries |
| Create | `docs/architecture/execution-manifest-schema.md` | Human-readable manifest contract |
| Create | `docs/architecture/execution-manifest.schema.yaml` | Machine-readable schema source for tests, including regeneration_command, replay_command, environment pin, input_residency, and output_residency |
| Create | `tests/fixtures/architecture/execution_manifest.yaml` | Concrete manifest fixture for tests; YAML fixture validates against `docs/architecture/execution-manifest.schema.yaml` |
| Create | `tests/fixtures/architecture/execution_routing_cases.yaml` | Routing/evidence fixture cases |
| Create | `docs/architecture/execution-routing-policy-view.md` | Derived/readable policy view that references `config/workstations/registry.yaml` and treats #2119/#1838/#2089 as open dependencies; it must not duplicate canonical machine identity/capability/provider fields |
| Create | `docs/architecture/execution-entry-point-inventory.md` | Inventory scripts, packages, prompts, review runners, legal scans, report builders, and content pipelines across the named repos with empirical enumeration evidence and redacted path display |
| Create | `docs/architecture/execution-follow-up-issue-backlog.md` | Exact `gh issue create --title ... --body-file ... --label ...` command blocks and body drafts for missing runners, registries, validators, adapters, or runtime enforcement; if not filed immediately, blocker reason is recorded |
| Create | `tests/architecture/test_execution_layer_contract.py` | Tests manifest fixtures and routing-policy invariants, not only markdown phrase presence |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_execution_manifest_required_fields | Manifest fixture documents source_ids, input_residency, output_residency, tool, machine/provider, outputs, validation, command_manifest, regeneration_command, replay_command, environment_pin, checksums, legal_scan_evidence, review_artifact_paths | YAML fixture derived from schema | missing required fields fail |
| test_execution_manifest_evidence_fields_complete | Manifest schema requires `regeneration_command`, `replay_command`, `environment_pin`, `checksums`, `test_evidence`, `legal_scan_evidence`, and `review_artifact_paths` | schema + fixture | each evidence field is present and non-empty where report handoff is claimed |
| test_no_execution_direct_publication | Execution outputs cannot set `report_eligible: true` without validation evidence and allowed output_residency | manifest fixtures | invalid direct-public fixture fails; valid evidence-backed fixture passes |
| test_routing_policy_references_workstation_registry | Routing policy view references canonical `config/workstations/registry.yaml` registry keys and does not duplicate identity/capability fields (`hostname`, `ip`, `os`, `roles`, license/provider capability fields) | routing policy + registry fixture | orphan IDs or duplicated machine/provider truth fail |
| test_validation_evidence_required_for_report_handoff | Report handoff requires tests/legal scan/checksums/review evidence according to output posture | manifest fixtures | missing evidence fails |
| test_residency_compatibility_matrix | `output_residency` cannot be more public than `input_residency` unless promotion gates are present | execution routing cases | invalid public/client/report handoffs fail closed |
| test_input_data_boundary_crosswalk | Input data is cross-referenced to data-layer `source_id`/`source_registry_kind` rows rather than duplicated; mounted sources must reference `mounted-source-registry.yaml`, repo/document-index/manual seed sources must reference their declared registry kind, and unresolved repo/client/wiki paths are blocked on #2731/#2732 | manifest fixtures + data-layer registry fixture | inline raw data, unknown source_id, missing applicable registry_ref, or unregistered repo/client/wiki path fails closed |
| test_execution_entry_point_inventory_covers_named_repos | Inventory contains evidence rows for workspace-hub plus available sibling/related repos or explicit unavailable markers, with redacted path display for client/project roots | inventory | no silent omissions or raw private path leakage |
| test_follow_up_issue_bundle_present | Missing runners/registries/validators/adapters/runtime enforcement have exact `gh issue create` commands and body drafts or no-action rationale | follow-up bundle | every gap accounted for |

---

## Acceptance Criteria
- [ ] Execution levels E-L1 through E-L4 are defined.
- [ ] Input data boundary is explicit: execution references/validates data-layer inputs but does not become the canonical owner of raw data.
- [ ] Routing policy view covers canonical registry keys (`dev-primary`, `dev-secondary`, licensed machine keys), local worktrees, background jobs, and provider tools as machine capabilities by referencing `config/workstations/registry.yaml`; #2119/#1838/#2089 remain open dependencies and must not be treated as approved routing policy.
- [ ] Execution evidence requirements include command manifests, regeneration commands, replay commands, environment pins, checksums, tests, legal scan, and adversarial review artifacts where applicable, and each required field has a matching schema/TDD assertion.
- [ ] Report-layer handoff requires validation evidence plus `input_residency` and `output_residency` metadata, and a residency-compatibility test fails closed when output is more public than input without promotion gates.
- [ ] Execution entry-point inventory includes empirical filesystem/git enumeration for each available named repo, records explicit unavailable/not-applicable evidence for missing repos, and redacts client/project child names in tracked public docs.
- [ ] Follow-up implementation work is represented by exact `gh issue create` command/body drafts in `docs/architecture/execution-follow-up-issue-backlog.md`; no implementation is embedded in this plan.
- [ ] Verification commands are explicit and must pass after implementation: `uv run pytest tests/architecture/test_execution_layer_contract.py -v` and `git add -N <new-files> && scripts/legal/legal-sanity-scan.sh --diff-only`.
- [ ] Revised plan receives substantive Claude/Codex re-review before approval request; Gemini must be substantive or explicitly `UNAVAILABLE` due quota, no unresolved MAJOR findings may remain, and the approval request cites revision-stamped non-empty artifact evidence rather than paths that can be truncated by the same review run.

---

## Revision / Adversarial Review Summary

Prior-cycle MAJOR disposition for this revision:

| Finding class | Disposition in this revision |
|---|---|
| Self-defeating same-cycle review citations | Header/artifact map cite only prior-cycle disagreement; current-cycle provider paths are generated after commit. |
| Routing-policy duplication under-specified | TDD row now names duplicated machine/provider field classes that must fail. |
| Missing residency-compatibility TDD | Added `test_residency_compatibility_matrix`. |
| Evidence fields not covered by tests | Added schema/TDD row for replay, env pin, checksums, legal scan, review artifacts. |
| Entry-point inventory redaction | Added redaction requirement to TDD and AC. |
| Source-ID universe undefined | TDD now requires known registry IDs or explicit fail-closed blockers on #2731/#2732. |
| Review gate as acceptance property | AC now states re-review requirement but not as a deliverable substitute; this disposition table is the artifact-property map. |
| Prior MAJORs not surfaced | This table maps prior MAJOR classes to current revision changes. |

Do not summarize in-progress/current-cycle provider artifacts inside this plan body; `plan-review-fanout.sh` truncates target provider files before writing them, so self-referential artifact tables produce false 0-byte evidence findings.

Current gate: after this exact committed plan path is pushed, run `scripts/review/plan-review-fanout.sh <plan>`, inspect non-empty provider artifacts in `scripts/review/results/`, and preserve/cite revision-stamped non-empty evidence in the approval request rather than relying on same-cycle paths that fanout may truncate. Gemini may be recorded as `UNAVAILABLE` during quota exhaustion, but Claude/Codex must return substantive artifacts and MAJOR findings must be cleared before any approval request.

---

## Risks and Open Questions
- **Risk:** Execution input data may be double-counted as data-layer and execution-layer ownership; contract must distinguish source ownership from executable input contract.
- **Risk:** Machine routing can drift quickly; matrix must point to canonical registry or include freshness date.
- **Decision for this packet:** execution manifest fixtures are YAML; markdown docs are human-readable contract views.
- **Decision:** Provider-agent prompts are E-L1 input-contract artifacts when they constrain work scope or tool behavior; provider stdout/stderr/review files are E-L4 validation/evidence artifacts. Both must reference data/report contracts rather than embedding raw private data.

---

## Complexity: T3
Execution architecture crosses data input contracts, code/tools, machines/providers, licensing, validation, and report handoff governance.
