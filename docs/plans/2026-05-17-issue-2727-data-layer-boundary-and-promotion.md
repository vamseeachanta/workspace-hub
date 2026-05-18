# Plan for #2727: Define data layer boundary and llm-wiki data promotion model

> **Status:** `status:plan-review` — revised after MAJOR review findings; pending re-review; not approved
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2727
> **Review artifacts:** `scripts/review/results/2026-05-17-plan-2727-claude.md`, `scripts/review/results/2026-05-17-plan-2727-codex.md`, `scripts/review/results/2026-05-17-plan-2727-gemini.md`, `scripts/review/results/2026-05-17-plan-2727-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/DATA_RESIDENCE_POLICY.md` — existing three-tier data model separates collection data (`worldenergydata`), engineering reference data (`digitalmodel`), and project/client data (`client_projects` / equivalent), with path-based handoff conventions and git/LFS/external-storage thresholds.
- Found: `data/document-index/mounted-source-registry.yaml` — existing mounted-source registry already enumerates local, remote, API, standards, literature, and project-document source roots, including `/mnt/local-analysis/workspace-hub`, `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/docs`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/remote/ace-linux-2/dde/*`, and `api://worldenergydata`.
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
- [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727) — issue body requests this architecture review and layer-specific scope.
- [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726) — parent architecture issue for data, execution, and report layer boundaries.
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
| `/mnt/local-analysis/<repo>/` | repo checkouts such as `workspace-hub`, documented tier-1 engineering/data repos (`digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`), and knowledge/publication/strategy repos (`llm-wiki`, `aceengineer-website`, `aceengineer-strategy`) | D-L3 curated knowledge/data or repo-backed execution/report metadata, depending on repo/path | Public-facing only for explicitly public repos/content; sanitized/curated data only | Public `llm-wiki` content, curated data, and sanitized fixtures belong here when repo policy allows; private raw source data should not be inferred public just because it was used to create a sanitized derivative. |

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
docs/DATA_RESIDENCE_POLICY.md:13-15 — Tier 1 Collection Data = `worldenergydata`; Tier 2 Engineering Reference Data = `digitalmodel`; Tier 3 Project Data = project repos/client_projects.
docs/DATA_RESIDENCE_POLICY.md:62 — project-specific configurations, analysis inputs/outputs, and client deliverables are never stored in `worldenergydata` or `digitalmodel`.
data/document-index/mounted-source-registry.yaml:5-48,163-183 — tracked source roots include `workspace_hub_local`, standards/literature mounts, project/docs mounts, API metadata virtual root, and ACMA codes local root.
docs/content-pipeline/README.md:3,27,51-58,99 — internal knowledge is transformed into client-facing content by stripping internal references/metadata and targeting zero internal references in output.
docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md:106-113 — documented Tier-1 core engineering repos are `digitalmodel`, `assetutilities`, `assethold`, and `worldenergydata`; other local repos require separate role classification.
config/workstations/registry.yaml:3 — all machine identity/capability data lives in this registry; execution routing docs must reference it instead of duplicating machine truth.
docs/BUSINESS_BRAIN.md:106-115 — knowledge promotion requires explicit source/provenance/license/legal gates and `scripts/legal/legal-sanity-scan.sh --diff-only` for reviewed diffs.
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
| This plan | `docs/plans/2026-05-17-issue-2727-data-layer-boundary-and-promotion.md` |
| Data layer contract | `docs/architecture/data-layer-contract.md` |
| Data source inventory matrix | `docs/architecture/data-source-inventory.md` plus structured fixture `tests/fixtures/architecture/data_source_inventory.yaml` |
| Promotion gates | `docs/architecture/llm-wiki-data-promotion-gates.md` |
| Tests | `tests/governance/test_data_layer_contract.py`; fixtures in `tests/fixtures/architecture/data_source_inventory.yaml` and `tests/fixtures/architecture/data_promotion_cases.yaml` |
| Review artifacts | `scripts/review/results/2026-05-17-plan-2727-*.md` |

---

## Deliverable
A data-layer contract will classify known data sources and define level-based promotion from raw/private/source data into raw-like staging, dedicated private client/domain corpora, and public `llm-wiki`/chatbot-ready content. Public-safe domain corpus can live in public `llm-wiki` after provenance/license/legal/sanitization gates. Private/domain/client corpora are only for restricted, client, licensed, embargoed, or otherwise non-public derivatives. Client insight reports may combine private client wiki corpora with public `llm-wiki` at retrieval/report runtime without merging private client data into the public corpus.

---

## Proposed Data Layer Levels
| Level | Working name | Contents | Public posture |
|---|---|---|---|
| D-L1 | Raw/source data | `/mnt` raw data, API downloads, standards/literature PDFs, client/project archives, repo raw datasets, generated raw extracts | Private/internal by default; no direct public/report use |
| D-L2 | Raw-like structured/staging data | inventories, source cards, extracted notes, document summaries, RAG chunks, source manifests, source classification packs | Controlled staging; may be local/private repo; not public by default |
| D-L3 | Curated knowledge data | sanitized `llm-wiki` markdown pages, public-safe source summaries, curated reference tables/fixtures | Public/chatbot eligible only after provenance/license/legal/sanitization review; public-safe domain corpus belongs in public `llm-wiki` |
| D-L4 | Derived indexes/search data | embeddings, search indexes, chatbot retrieval corpora, freshness scorecards | Public/private matches underlying corpus; regeneration manifest and output_residency required |

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
    document required fail-closed public llm-wiki/chatbot eligibility gates and defer runtime enforcement to filed follow-up issue unless implemented in this packet
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/data-layer-contract.md` | Defines data layer levels and boundaries |
| Create | `tests/fixtures/architecture/data_source_inventory.yaml` | Structured source of truth for schema tests; markdown inventory is a readable generated/curated view and must cross-link to existing `data/document-index/mounted-source-registry.yaml` without replacing it |
| Create | `tests/fixtures/architecture/data_promotion_cases.yaml` | Fixture cases for public-safe, private-domain, and client-private promotion routing |
| Create | `docs/architecture/data-source-inventory.md` | Human-readable source/source-class matrix for user curation; required columns: source_class, allowed_artifacts, forbidden_artifacts, canonical_home, retention_rule, publication_rule, owner, source_id/path, provenance, license_posture, sensitivity, promotion_gate, output_residency |
| Create | `docs/architecture/data-boundary-violations-and-gaps.md` | Inventory of existing artifacts that violate or blur raw/staged/public/client boundaries, plus actual `gh issue create` commands/body drafts for follow-up issues when not filed immediately |
| Create | `docs/architecture/llm-wiki-data-promotion-gates.md` | Defines D-L1→D-L2→D-L3/D-L4 promotion rules |
| Create | `tests/governance/test_data_layer_contract.py` | Guards inventory/schema behavior using fixtures, not only markdown phrase presence |
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
| test_every_source_has_owner_and_provenance | Each source class has owner/canonical path or source_id and provenance posture | inventory fixture parsed from source matrix | no blanks in required fields |
| test_inventory_has_bucket_contract_columns | Each bucket/source class declares allowed_artifacts, forbidden_artifacts, canonical_home, retention_rule, publication_rule, and output_residency | inventory fixture parsed from source matrix | missing columns/blank cells fail |
| test_boundary_violation_inventory_present | Existing artifacts that violate or blur boundaries are listed or explicitly marked none-found with search evidence | gap inventory | no un-evidenced omission |
| test_follow_up_issue_backlog_present | Gap inventory contains proposed follow-up GitHub issue titles/scopes for storage, registries, freshness scans, and promotion gates | gap inventory | each gap has issue proposal or explicit no-action rationale |
| test_generated_indexes_inherit_corpus_posture | D-L4 indexes cannot be more public than source corpus | inventory fixture | violations fail |

---

## Acceptance Criteria
- [ ] Data levels D-L1 through D-L4 are defined and reconciled with existing data residence tiers.
- [ ] Initial source inventory includes `/mnt` roots, tier-1 repos, `worldenergydata` public sources, `digitalmodel` reference data, mounted standards/literature, client/project data, private/raw `llm-wiki`, public `llm-wiki`, and derived indexes.
- [ ] Data source inventory includes concrete path-class examples for `/mnt/ace/` raw PDFs → markdown, `/mnt/ace/raw-processed/` private staging/indexes/uncurated wiki material, and `/mnt/local-analysis/<repo>/` repo-backed public-facing/curated surfaces, without assuming every local checkout is tier-1.
- [ ] `llm-wiki` raw/staging vs public-facing content boundaries are explicit.
- [ ] Client/project data is handled as a distinct class: verified-present raw client roots and explicitly planned/unavailable client roots are separated; planned roots and `/mnt/local-analysis/<client>-llm-wiki` private repositories are provisioning targets, not assumed-existing resources, and must be filed as follow-up issues before implementation can rely on them.
- [ ] Insight reports can combine private client `llm-wiki` corpora with public `llm-wiki` retrieval, but public and private source classes remain separated and client data is non-public by default.
- [ ] Promotion gates include provenance, license/legal, sanitization, technical review, freshness/regeneration metadata, and output_residency.
- [ ] Data source inventory includes allowed artifacts, forbidden artifacts, canonical home, retention rule, and publication rule for every bucket.
- [ ] Boundary violation/gap inventory identifies existing blurred-boundary artifacts or explicitly records none-found with search evidence.
- [ ] Follow-up implementation work is proposed as GitHub issue titles/scopes in `docs/architecture/data-boundary-violations-and-gaps.md`; no implementation is embedded in this plan.
- [ ] Verification commands are explicit and must pass after implementation: `uv run pytest tests/governance/test_data_layer_contract.py -v` and `scripts/legal/legal-sanity-scan.sh --diff-only`.
- [ ] Revised plan receives Claude, Codex, and Gemini re-review before approval request.

---

## Adversarial Review Summary
Prior review artifacts exist under `scripts/review/results/2026-05-17-plan-*.md`; this revision is pending a fresh post-push re-review via `scripts/review/plan-review-fanout.sh`.

| Provider | Artifact | Verdict |
|---|---|---|
| Claude | `scripts/review/results/2026-05-17-plan-2727-claude.md` | MAJOR |
| Codex | `scripts/review/results/2026-05-17-plan-2727-codex.md` | MAJOR |
| Gemini | `scripts/review/results/2026-05-17-plan-2727-gemini.md` | MAJOR |
| Disagreement report | `scripts/review/results/2026-05-17-plan-2727-disagreement.md` | MAJOR findings consolidated |

Prior review artifacts contained MAJOR findings and are superseded by this revision. Do not ask for user approval, implement, or mark `status:plan-approved` until this exact committed plan path is pushed, Claude/Codex/Gemini re-review artifacts are non-empty (or a provider is explicitly marked UNAVAILABLE), and MAJOR findings are cleared.

---

## Risks and Open Questions
- **Risk:** Existing data residence tiers and proposed data-layer levels can be confused; implementation must use clear names and crosswalk table.
- **Risk:** Some `/mnt` inventories can expose client identifiers; tracked public docs must use redacted source IDs or private-only appendices for raw client path names.
- **Open:** Canonical home for D-L2 raw-like `llm-wiki` staging: private repo, workspace-hub staging, or public `llm-wiki` private branch? This must be resolved against `mounted-source-registry.yaml`; no new inventory may fork the registry.
- **Open:** Which data sources should be considered chatbot-eligible by default after D-L3 promotion?

---

## Complexity: T3
Data governance crosses public/private repos, local mounts, client/project archives, llm-wiki, RAG/chatbot indexes, and legal/sanitization gates.
