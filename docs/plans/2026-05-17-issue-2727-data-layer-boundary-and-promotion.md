# Plan for #2727: Define data layer boundary and llm-wiki data promotion model

> **Status:** draft — user source-curation pass pending; not adversarial-reviewed; not `status:plan-review`
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2727
> **Review artifacts:** pending after user source-curation pass

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
- [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) — issue body requests this architecture review and layer-specific scope.
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
| Client/project data | `/mnt/ace/rock-oil-field`; `/mnt/ace/client-projects`; `/mnt/ace/doris`; `/mnt/ace/acma-projects`; `/mnt/ace/frontier-deepwater`; `/mnt/ace/saipem`; similar client roots | Unique private-client class; promote only to dedicated private `/mnt/local-analysis/<client>-llm-wiki` repos/corpora; sanitized derivatives require explicit approval |
| `llm-wiki` raw-like data | source inventories, extracted notes, staging packs, source cards, provenance metadata, RAG indexes | Private/local or controlled staging until reviewed |
| Public `llm-wiki` content | sanitized markdown pages and public chatbot/search corpus | Public-facing after source/legal/sanitization gates |
| Execution artifacts | issue plans, YAML/JSON configs, prompt bundles, tool manifests, run logs, checksums | Execution/report boundary; promote only manifests/evidence, not bulky generated data by default |
| Report artifacts | internal reports, client HTML, limited PDFs, chatbot/query configs/indexes | Report layer; audience-specific evidence and sanitization gates required |

### Concrete example path classes for user review
| Example path / pattern | Example contents | Data layer level | Public/private posture | Notes |
|---|---|---|---|---|
| `/mnt/ace/` raw PDFs → generated `.md` files | Standards/literature/project PDFs and their first-pass markdown extraction outputs | D-L1 raw/source data → D-L2 raw-like extraction output | Private/local source data | Treat the PDFs and unreviewed markdown as local/private source material; no direct public `llm-wiki` or client-report eligibility without promotion gates. |
| `/mnt/ace/raw-processed/` | Index files, markdown files, uncurated `llm-wiki` drafts/staging packs, extraction manifests | D-L2 raw-like structured/staging data | Private/local source data | Treat as staging and curation workspace; useful for source cards, inventories, RAG chunks, and reviewer work queues, but not public by default. |
| `/mnt/local-analysis/<repo>/` | Tier-1 repo checkouts such as `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`, `aceengineer-website`, `aceengineer-strategy` | D-L3 curated knowledge/data or repo-backed execution/report metadata, depending on repo/path | Public-facing only for explicitly public repos/content; sanitized/curated data only | Public `llm-wiki` content, curated data, and sanitized fixtures belong here when repo policy allows; private raw source data should not be inferred public just because it was used to create a sanitized derivative. |

### Client data handling model
| Raw client source path / pattern | Intended private knowledge repo | Data layer level | Public/private posture | Insight-report use |
|---|---|---|---|---|
| `/mnt/ace/rock-oil-field` | `/mnt/local-analysis/rock-oil-field-llm-wiki` | D-L1 client raw/source → D-L2/D-L3 private client wiki | Private client data; private repo required | Combine private client wiki with public `llm-wiki` only at retrieval/report runtime to produce controlled insight reports. |
| `/mnt/ace/client-projects` | `/mnt/local-analysis/client-projects-llm-wiki` | D-L1 client raw/source → D-L2/D-L3 private client wiki | Private client data; private repo required | Same: private corpus remains separate; reports cite private/public source classes distinctly. |
| `/mnt/ace/doris` | `/mnt/local-analysis/doris-llm-wiki` | D-L1 client raw/source → D-L2/D-L3 private client wiki | Private client data; private repo required | Use as client-specific retrieval corpus alongside public `llm-wiki`, not as public `llm-wiki` content. |
| `/mnt/ace/acma-projects` | `/mnt/local-analysis/acma-projects-llm-wiki` | D-L1 client raw/source → D-L2/D-L3 private client wiki | Private client data; private repo required | Use for private project insight reports; sanitized learnings require separate approval before public reuse. |
| `/mnt/ace/frontier-deepwater` | `/mnt/local-analysis/frontier-deepwater-llm-wiki` | D-L1 client raw/source → D-L2/D-L3 private client wiki | Private client data; private repo required | Use as private corpus for insight/report generation with explicit access controls. |
| `/mnt/ace/saipem` and similar client roots | `/mnt/local-analysis/<client>-llm-wiki` | D-L1 client raw/source → D-L2/D-L3 private client wiki | Private client data; private repo required | Pattern for future client corpora; never merge raw/private client content into public `llm-wiki`. |

Client data is handled uniquely from general `/mnt/ace` raw/staging data: every client raw root should promote into a dedicated private `/mnt/local-analysis/<client>-llm-wiki` repository/corpus, not into the public `llm-wiki`. Insight reports may combine retrieval from the private client wiki plus the public `llm-wiki`, but the report-generation layer must preserve source-class boundaries, access controls, and sanitization gates.

### Gaps identified
- No approved level taxonomy yet for data L1 raw → L2 raw-llm-wiki/staging → L3 public `llm-wiki`/chatbot knowledge.
- No approved level taxonomy yet for execution inputs vs data-layer inputs, code/tooling, machines/compute, validation evidence, and handoff manifests.
- No approved level taxonomy yet for report raw outputs, data outputs, HTML/PDF/report formats, interactivity, and chatbot surfaces.
- No canonical matrix yet mapping source class → owner repo/path → public/private posture → promotion gate → report/chatbot eligibility.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-17T01:12:21Z via `gh issue view`):
- `#2727` — OPEN — feat(architecture): define data layer boundary and llm-wiki data promotion model
- `#2726` — OPEN — feat(architecture): review data, execution, and report layer boundaries

**File existence / evidence sources**:
- EXISTS: `docs/DATA_RESIDENCE_POLICY.md`
- EXISTS: `data/document-index/mounted-source-registry.yaml`
- EXISTS: `docs/content-pipeline/README.md`
- EXISTS: `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
- Path probe 2026-05-17: `/mnt/ace/` exists on this host; `/mnt/ace/raw-processed/` is recorded as user-provided intended/example staging path but was not present in this runtime probe; `/mnt/local-analysis/` exists and contains at least `workspace-hub`, `llm-wiki`, and `digitalmodel` checkouts in this runtime.
- Client path probe 2026-05-17: `/mnt/ace/rock-oil-field`, `/mnt/ace/doris`, `/mnt/ace/acma-projects`, and `/mnt/ace/saipem` exist on this host; `/mnt/ace/client-projects` and `/mnt/ace/frontier-deepwater` are recorded as user-provided intended/example client roots but were not present in this runtime probe; the corresponding `/mnt/local-analysis/<client>-llm-wiki` private repo paths were not present in this runtime probe and should be treated as planned/private target repositories unless separately created.

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
| This plan | `docs/plans/2026-05-17-issue-2727-data-layer-boundary-and-promotion.md` |
| Data layer contract | `docs/architecture/data-layer-contract.md` |
| Data source inventory matrix | `docs/architecture/data-source-inventory.md` |
| Promotion gates | `docs/architecture/llm-wiki-data-promotion-gates.md` |
| Tests | `tests/architecture/test_data_layer_contract.py` |
| Review artifacts | `scripts/review/results/2026-05-17-plan-2727-*.md` |

---

## Deliverable
A data-layer contract will classify known data sources and define level-based promotion from raw/private/source data into raw-like `llm-wiki` staging, dedicated private client `llm-wiki` repositories, and public `llm-wiki`/chatbot-ready content. Client insight reports must combine private client wiki corpora with public `llm-wiki` at retrieval/report runtime without merging private client data into the public corpus.

---

## Proposed Data Layer Levels
| Level | Working name | Contents | Public posture |
|---|---|---|---|
| D-L1 | Raw/source data | `/mnt` raw data, API downloads, standards/literature PDFs, client/project archives, repo raw datasets, generated raw extracts | Private/internal by default; no direct public/report use |
| D-L2 | Raw-like structured/staging data | inventories, source cards, extracted notes, document summaries, RAG chunks, source manifests, source classification packs | Controlled staging; may be local/private repo; not public by default |
| D-L3 | Curated knowledge data | sanitized `llm-wiki` markdown pages, public-safe source summaries, curated reference tables/fixtures | Public/chatbot eligible only after provenance/license/sanitization review |
| D-L4 | Derived indexes/search data | embeddings, search indexes, chatbot retrieval corpora, freshness scorecards | Public/private matches underlying corpus; regeneration manifest required |

---

## Pseudocode
```text
function classify_data_source(source):
    detect origin: public API, engineering standard, literature, repo data, client/project, generated artifact
    assign data residence tier from existing policy
    assign data layer level D-L1..D-L4
    record canonical owner and path/source_id
    record provenance, license, sensitivity, regeneration command, last-known-good
    define permitted next promotion target and required gates
    block public llm-wiki/chatbot eligibility unless gates are satisfied
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/data-layer-contract.md` | Defines data layer levels and boundaries |
| Create | `docs/architecture/data-source-inventory.md` | Initial known source/source-class matrix for user curation |
| Create | `docs/architecture/llm-wiki-data-promotion-gates.md` | Defines D-L1→D-L2→D-L3/D-L4 promotion rules |
| Create | `tests/architecture/test_data_layer_contract.py` | Guards required columns and private/public defaults |
| Update | `docs/DATA_RESIDENCE_POLICY.md` | Cross-link layer levels after approval |
| Update | `docs/plans/README.md` | Plan index entry |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_data_inventory_required_seed_sources | Seed source classes from this plan exist in the inventory | `data-source-inventory.md` | all seed classes present |
| test_private_sources_default_non_public | Client/project/mounted private sources default to non-public | inventory rows | no public eligibility without gates |
| test_client_sources_require_private_client_wiki | Client raw roots map to `/mnt/local-analysis/<client>-llm-wiki` private repos, not public `llm-wiki` | inventory rows | client rows require private target repo and explicit report-combine rule |
| test_raw_to_public_requires_intermediate_gate | D-L1 cannot promote directly to public D-L3 without D-L2 review metadata | promotion rules | direct paths fail |
| test_every_source_has_owner_and_provenance | Each source class has owner/canonical path or source_id and provenance posture | inventory | no blanks in required fields |
| test_generated_indexes_inherit_corpus_posture | D-L4 indexes cannot be more public than source corpus | inventory | violations fail |

---

## Acceptance Criteria
- [ ] Data levels D-L1 through D-L4 are defined and reconciled with existing data residence tiers.
- [ ] Initial source inventory includes `/mnt` roots, tier-1 repos, `worldenergydata` public sources, `digitalmodel` reference data, mounted standards/literature, client/project data, private/raw `llm-wiki`, public `llm-wiki`, and derived indexes.
- [ ] Data source inventory includes concrete path-class examples for `/mnt/ace/` raw PDFs → markdown, `/mnt/ace/raw-processed/` private staging/indexes/uncurated wiki material, and `/mnt/local-analysis/<repo>/` tier-1 public-facing repos with curated/sanitized data.
- [ ] `llm-wiki` raw/staging vs public-facing content boundaries are explicit.
- [ ] Client/project data is handled as a distinct class: raw client roots such as `/mnt/ace/rock-oil-field`, `/mnt/ace/client-projects`, `/mnt/ace/doris`, `/mnt/ace/acma-projects`, `/mnt/ace/frontier-deepwater`, and `/mnt/ace/saipem` promote only into dedicated private `/mnt/local-analysis/<client>-llm-wiki` repositories/corpora.
- [ ] Insight reports can combine private client `llm-wiki` corpora with public `llm-wiki` retrieval, but public and private source classes remain separated and client data is non-public by default.
- [ ] Promotion gates include provenance, license/legal, sanitization, technical review, and freshness/regeneration metadata.
- [ ] Validation tests and legal scan are planned before implementation.
- [ ] Plan receives adversarial review before `status:plan-review`.

---

## Adversarial Review Summary
Pending. Do not move to `status:plan-review` until user source-curation pass and adversarial review are complete.

---

## Risks and Open Questions
- **Risk:** Existing data residence tiers and proposed data-layer levels can be confused; implementation must use clear names and crosswalk table.
- **Risk:** Some `/mnt` inventories can expose client identifiers; source IDs and redaction are required in public-facing docs.
- **Open:** Canonical home for D-L2 raw-like `llm-wiki` staging: private repo, workspace-hub staging, or public `llm-wiki` private branch?
- **Open:** Which data sources should be considered chatbot-eligible by default after D-L3 promotion?

---

## Complexity: T3
Data governance crosses public/private repos, local mounts, client/project archives, llm-wiki, RAG/chatbot indexes, and legal/sanitization gates.
