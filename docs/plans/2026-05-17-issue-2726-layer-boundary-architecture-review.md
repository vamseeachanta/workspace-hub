# Plan for #2726: Review data, execution, and report layer boundaries

> **Status:** `status:plan-review` — re-reviewed 2026-05-17; awaiting user decision; not approved
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2726
> **Review artifacts:** `scripts/review/results/2026-05-17-plan-2726-claude.md`, `scripts/review/results/2026-05-17-plan-2726-codex.md`, `scripts/review/results/2026-05-17-plan-2726-gemini.md`, `scripts/review/results/2026-05-17-plan-2726-disagreement.md`

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
- [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726) — issue body requests this architecture review and layer-specific scope.
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
- `#2726` — OPEN — feat(architecture): review data, execution, and report layer boundaries
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
| This plan | `docs/plans/2026-05-17-issue-2726-layer-boundary-architecture-review.md` |
| Data-layer child plan | `docs/plans/2026-05-17-issue-2727-data-layer-boundary-and-promotion.md` |
| Execution-layer child plan | `docs/plans/2026-05-17-issue-2728-execution-layer-contracts-routing.md` |
| Report-layer child plan | `docs/plans/2026-05-17-issue-2729-report-layer-outputs-evidence.md` |
| Target architecture contract | `docs/architecture/data-execution-report-layer-contract.md` |
| Source classification matrix | `docs/architecture/source-layer-classification-matrix.md` |
| Review artifacts | `scripts/review/results/2026-05-17-plan-2726-*.md` |

---

## Deliverable
A reviewed architecture contract will define the repo ecosystem's data, execution, and report layers; level taxonomy per layer; canonical source classes; promotion gates; and ownership boundaries across `/mnt` data, client/project data, tier-1 repos, public/private `llm-wiki`, execution machines, and report/chatbot surfaces.

---

## Pseudocode
```text
function build_layer_contract():
    inventory known source classes from registry, repo docs, issues, and user-added sources
    assign each source class to a data/execution/report layer and level
    define allowed transitions between layers
    define required gates for each transition: provenance, license/legal, sanitization, tests, review
    define canonical owner repo/path and fallback behavior for unavailable mounts
    define report/chatbot eligibility rules from data classification and evidence state
    publish architecture contract plus source matrix
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/data-execution-report-layer-contract.md` | Main architecture contract |
| Create | `docs/architecture/source-layer-classification-matrix.md` | Reviewable initial source inventory and level assignment |
| Update | `docs/DATA_RESIDENCE_POLICY.md` | Cross-link expanded architecture; do not replace existing policy without review |
| Update | `docs/content-pipeline/README.md` | Align publication/report-layer language if approved |
| Update | `docs/plans/README.md` | Plan index entry |
| Create/Update | child issue plan artifacts | Keep layer-specific details independently reviewable |

---

## TDD / Validation List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_source_matrix_has_required_columns | Source matrix has source_class, owner, canonical_path, layer, level, public_posture, promotion_gate | architecture matrix markdown/csv | all required columns present |
| test_private_sources_not_public_eligible_by_default | Client/mounted/private roots cannot map directly to public `llm-wiki` or client report without gates | source matrix | violations fail |
| test_layer_transitions_are_explicit | Every data→execution→report path names required gates | layer contract | no implicit promotion paths |
| test_known_sources_are_classified | Initial known sources from this plan are represented | source matrix | all seed classes present |
| test_legal_scan_passes | Contract and matrix avoid client identifiers/secrets | plan/docs paths | legal sanity scan passes |

---

## Acceptance Criteria
- [ ] Child plans for [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727), [#2728](https://github.com/vamseeachanta/workspace-hub/issues/2728), and [#2729](https://github.com/vamseeachanta/workspace-hub/issues/2729) are source-curated and reviewed.
- [ ] Architecture contract defines level taxonomy for data, execution, and report layers.
- [ ] Initial known source classes include `/mnt` data, client/project data, all tier-1 repo data, public/private `llm-wiki`, execution artifacts, and report/chatbot artifacts.
- [ ] Matrix defines owner repo/path, public/private posture, promotion gate, and report/chatbot eligibility for each source class.
- [ ] Legal/security scan passes for all created docs.
- [ ] Adversarial plan review artifacts exist before applying `status:plan-review`.
- [ ] No implementation or publication changes occur before user approval.

---

## Adversarial Review Summary
Re-reviewed on 2026-05-17 with Claude, Codex, and Gemini via `scripts/review/plan-review-fanout.sh`.

| Provider | Artifact | Verdict |
|---|---|---|
| Claude | `scripts/review/results/2026-05-17-plan-2726-claude.md` | MAJOR |
| Codex | `scripts/review/results/2026-05-17-plan-2726-codex.md` | MAJOR |
| Gemini | `scripts/review/results/2026-05-17-plan-2726-gemini.md` | MAJOR |
| Disagreement report | `scripts/review/results/2026-05-17-plan-2726-disagreement.md` | MAJOR findings consolidated |

Plan is in `status:plan-review` for user review only. Do not implement or mark `status:plan-approved` until the user explicitly approves a revised plan.

---

## Risks and Open Questions
- **Risk:** Data-level names may conflict with existing `DATA_RESIDENCE_POLICY.md` tier names. Plan must either reconcile terms or use distinct labels (`layer level` vs `data residence tier`).
- **Risk:** Mounted project/source paths can contain sensitive client names; inventories must support redaction and source IDs.
- **Open:** Should execution input data be classified primarily under data layer, execution layer, or both via an input-contract boundary?
- **Open:** Which repo is canonical for private `llm-wiki` raw/staging content if not the public `llm-wiki` repo?

---

## Complexity: T3
Multi-repo, multi-layer architecture/governance issue with sensitive-data, public/private publication, compute-routing, and chatbot/reporting implications.
