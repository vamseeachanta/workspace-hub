# Plan for #2728: Define execution layer contracts, tooling, and compute routing

> **Status:** `status:plan-review` — re-reviewed 2026-05-17; awaiting user decision; not approved
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2728
> **Review artifacts:** `scripts/review/results/2026-05-17-plan-2728-claude.md`, `scripts/review/results/2026-05-17-plan-2728-codex.md`, `scripts/review/results/2026-05-17-plan-2728-gemini.md`, `scripts/review/results/2026-05-17-plan-2728-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/DATA_RESIDENCE_POLICY.md` — existing three-tier data model separates collection data (`worldenergydata`), engineering reference data (`digitalmodel`), and project/client data (`client_projects` / equivalent), with path-based handoff conventions and git/LFS/external-storage thresholds.
- Found: `data/document-index/mounted-source-registry.yaml` — existing mounted-source registry already enumerates local, remote, API, standards, literature, and project-document source roots, including `/mnt/local-analysis/workspace-hub`, `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/docs`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/remote/ace-linux-2/dde/*`, and `api://worldenergydata`.
- Found: `docs/content-pipeline/README.md` — existing source → transform → stage → review → publish pipeline for turning internal wiki/source material into public/client-facing website content.
- Found: `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — current repo ecosystem summary names workspace-hub as control plane, tier-1 repos, skills, scripts, document-intelligence, llm-wiki, and report/docs locations.
- Gap: No single current architecture contract defines the data → execution → report layer boundaries across `/mnt` data, client project data, all tier-1 repo data, public/private `llm-wiki`, execution machines, and report/chatbot surfaces.

### Standards
| Standard | Status | Source |
|---|---|---|
| Repo workflow hard gates | applicable | `AGENTS.md`; `docs/plans/README.md` |
| Data residence | applicable but needs expansion | `docs/DATA_RESIDENCE_POLICY.md` |
| Legal/security scan | applicable | `scripts/legal/legal-sanity-scan.sh` |

### LLM Wiki pages consulted
- `llm-wiki/` sibling and nested repo presence was detected via filesystem search; this plan will inventory canonical public/private wiki storage rather than assuming current clone layout is authoritative.
- `docs/content-pipeline/README.md` lists existing internal wiki sources and publication transform rules that strip internal references before public publication.

### Documents consulted
- [#2728](https://github.com/vamseeachanta/workspace-hub/issues/2728) — issue body requests this architecture review and layer-specific scope.
- [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726) — parent architecture issue for data, execution, and report layer boundaries.
- `docs/DATA_RESIDENCE_POLICY.md` — current data residence policy and examples.
- `data/document-index/mounted-source-registry.yaml` — known mounted/API source roots.
- `docs/content-pipeline/README.md` — current internal knowledge to public website pipeline.
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md` — current ecosystem inventory summary.

### Initial known data/source classes to include in the architecture
| Source class | Initial known examples / roots | Initial disposition |
|---|---|---|
| `/mnt` workspace/control-plane data | `/mnt/local-analysis/workspace-hub`; sibling tier-1 checkouts under `/mnt/local-analysis/`; worktrees under `/mnt/local-analysis/worktrees/` | Repo/control-plane evidence; inventory without assuming all paths are canonical |
| Tier-1 repo data | `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`, `aceengineer-website`, `aceengineer-strategy` | Repo-backed data/config/docs; classify by owner repo and public/private posture |
| Public collection data | `worldenergydata` APIs/sources: BSEE, SODIR, NDBC, MarineTraffic, marine safety incidents, oil prices, LNG terminals | Data-layer L1/L2 candidates; raw not committed unless policy allows |
| Engineering reference data | `digitalmodel` reference tables; standards-derived constants; SN curves; steel grades; hydrodynamic coefficients | Data-layer curated/reference; must carry provenance/license/citation sidecars where applicable |
| Mounted standards/literature | `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/acma-codes`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/remote/ace-linux-2/dde/*` | Reference-in-place; never blindly copy into public repos |
| Client/project data | `client_projects` / project repos / mounted project archives / local client folders | Private by default; sanitized derivatives only |
| `llm-wiki` raw-like data | source inventories, extracted notes, staging packs, source cards, provenance metadata, RAG indexes | Private/local or controlled staging until reviewed |
| Public `llm-wiki` content | sanitized markdown pages and public chatbot/search corpus | Public-facing after source/legal/sanitization gates |
| Execution artifacts | issue plans, YAML/JSON configs, prompt bundles, tool manifests, run logs, checksums | Execution/report boundary; promote only manifests/evidence, not bulky generated data by default |
| Report artifacts | internal reports, client HTML, limited PDFs, chatbot/query configs/indexes | Report layer; audience-specific evidence and sanitization gates required |

### Gaps identified
- No approved level taxonomy yet for data L1 raw → L2 raw-llm-wiki/staging → L3 public `llm-wiki`/chatbot knowledge.
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
DATA_RESIDENCE_POLICY.md: Tier 1 Collection Data = worldenergydata; Tier 2 Engineering Reference Data = digitalmodel; Tier 3 Project Data = project repos/client_projects.
DATA_RESIDENCE_POLICY.md: Raw API downloads and ZIP archives are never committed; pipeline scripts/configs and small reference data can be committed under policy.
mounted-source-registry.yaml: source roots include workspace_hub_local, ace_standards_local, og_standards_local, ace_project_local, research_literature_local, DDE remote roots, api_metadata_virtual, and acma_codes_local.
content-pipeline/README.md: Source wiki markdown is transformed, staged, reviewed, then published; transform strips internal references and metadata before publication.
```

**Gap proofs**:
- `docs/plans/` search for issue numbers 2726-2729 returned no existing plan files before this drafting wave.
- Existing policies cover important pieces but not the full cross-layer architecture and level taxonomy requested here.

**Reproduction proofs**:
N/A — architecture/governance planning issue, not a runtime failure.

<!-- Distinct sources: issue body, parent issue, DATA_RESIDENCE_POLICY, mounted-source-registry, content-pipeline README, capabilities summary. -->


---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-17-issue-2728-execution-layer-contracts-routing.md` |
| Execution layer contract | `docs/architecture/execution-layer-contract.md` |
| Execution input/output manifest schema | `docs/architecture/execution-manifest-schema.md` |
| Machine/tool routing matrix | `docs/architecture/execution-routing-matrix.md` |
| Tests | `tests/architecture/test_execution_layer_contract.py` |
| Review artifacts | `scripts/review/results/2026-05-17-plan-2728-*.md` |

---

## Deliverable
An execution-layer contract will define how input data contracts, code/tools, agents, machines/compute, validation, and evidence manifests transform data-layer sources into report-layer eligible artifacts without bypassing gates.

---

## Proposed Execution Layer Levels
| Level | Working name | Contents | Boundary rule |
|---|---|---|---|
| E-L1 | Input contracts | YAML/JSON specs, issue plans, source manifests, fixture manifests, prompt bundles | References data sources by source_id/path; does not own raw data |
| E-L2 | Tools/code execution | ingestion scripts, parsers, report generators, validation harnesses, legal scanners, skills/prompts | Code is repo-backed; Python via `uv run`; outputs manifest evidence |
| E-L3 | Compute/runtime placement | ace-linux-1, ace-linux-2, licensed Windows/machines, local worktrees, background jobs, provider agents | Routing matrix declares capability, data access, license, and security posture |
| E-L4 | Validation/evidence | tests, legal scan outputs, adversarial review artifacts, checksums, run manifests, command logs | Required handoff to report layer; raw logs remain internal unless sanitized |

---

## Pseudocode
```text
function execute_pipeline(execution_manifest):
    validate manifest schema and declared data source_ids
    verify source availability and permission posture
    route work to capable machine/provider/tool based on routing matrix
    run tools using repo-backed commands and isolated workdirs/worktrees
    collect tests, legal scan, checksums, output manifest, and review artifacts
    mark outputs report-eligible only if validation/evidence gates pass
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/execution-layer-contract.md` | Defines execution levels and layer boundaries |
| Create | `docs/architecture/execution-manifest-schema.md` | Describes input/output manifest fields |
| Create | `docs/architecture/execution-routing-matrix.md` | Maps tools/machines/providers to allowed source classes and outputs |
| Create | `tests/architecture/test_execution_layer_contract.py` | Ensures manifest/routing docs carry required fields and no direct publish path |
| Update | `config/workstations/registry.yaml` | Cross-link only if needed after approval; do not change machine routing in plan stage |
| Update | `docs/plans/README.md` | Plan index entry |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_execution_manifest_required_fields | Manifest documents input source IDs, tool, machine/provider, outputs, validation, evidence | schema doc | all required fields present |
| test_no_execution_direct_publication | Execution contract forbids raw output direct-to-public/report path | contract | direct publish wording absent/blocked |
| test_routing_matrix_has_capability_and_data_access | Each machine/provider row has capability, data access, license/security constraints | routing matrix | required columns present |
| test_validation_evidence_required_for_report_handoff | Report eligibility depends on validation/evidence artifacts | contract/schema | explicit gate present |
| test_input_data_boundary_crosswalk | Input data is cross-referenced to data-layer source IDs rather than duplicated | schema | source_id/path reference requirement present |

---

## Acceptance Criteria
- [ ] Execution levels E-L1 through E-L4 are defined.
- [ ] Input data boundary is explicit: execution references/validates data-layer inputs but does not become the canonical owner of raw data.
- [ ] Routing matrix covers ace-linux-1, ace-linux-2, licensed machines, local worktrees, background jobs, and provider agents at the class level.
- [ ] Execution evidence requirements include command manifests, checksums, tests, legal scan, and adversarial review artifacts where applicable.
- [ ] Report-layer handoff requires validation evidence and audience/posture metadata.
- [ ] Validation tests and legal scan are planned before implementation.
- [ ] Plan receives adversarial review before `status:plan-review`.

---

## Adversarial Review Summary
Re-reviewed on 2026-05-17 with Claude, Codex, and Gemini via `scripts/review/plan-review-fanout.sh`.

| Provider | Artifact | Verdict |
|---|---|---|
| Claude | `scripts/review/results/2026-05-17-plan-2728-claude.md` | MAJOR |
| Codex | `scripts/review/results/2026-05-17-plan-2728-codex.md` | MAJOR |
| Gemini | `scripts/review/results/2026-05-17-plan-2728-gemini.md` | MAJOR |
| Disagreement report | `scripts/review/results/2026-05-17-plan-2728-disagreement.md` | MAJOR findings consolidated |

Plan is in `status:plan-review` for user review only. Do not implement or mark `status:plan-approved` until the user explicitly approves a revised plan.

---

## Risks and Open Questions
- **Risk:** Execution input data may be double-counted as data-layer and execution-layer ownership; contract must distinguish source ownership from executable input contract.
- **Risk:** Machine routing can drift quickly; matrix must point to canonical registry or include freshness date.
- **Open:** Should execution manifests be markdown, YAML, or both?
- **Open:** Should provider-agent prompts be first-class execution artifacts or only evidence attachments?

---

## Complexity: T3
Execution architecture crosses data input contracts, code/tools, machines/providers, licensing, validation, and report handoff governance.
