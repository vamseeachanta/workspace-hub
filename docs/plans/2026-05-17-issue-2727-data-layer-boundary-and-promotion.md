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
- Found: `data/document-index/mounted-source-registry.yaml` — existing mounted-source registry already enumerates local, remote, API, standards, literature, and project-document source roots, including `/mnt/local-analysis/workspace-hub`, `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/docs`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/ace/docs/literature/dde (preferred migrated local copy; remote DDE is archival per mounted-source-registry.yaml)`, and `api://worldenergydata`.
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
| Mounted standards/literature | `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/acma-codes`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/ace/docs/literature/dde (preferred migrated local copy; remote DDE is archival per mounted-source-registry.yaml)` | Reference-in-place; never blindly copy into public repos |
| Client/project data | `[REDACTED-CLIENT-ROOT]`; `[REDACTED-CLIENT-ROOT]`; `[REDACTED-CLIENT-ROOT]`; `[REDACTED-CLIENT-ROOT]`; `[REDACTED-CLIENT-ROOT]`; `[REDACTED-CLIENT-ROOT]`; similar client roots | Unique private-client class; promote only to dedicated private `/mnt/local-analysis/<client>-llm-wiki` repos/corpora; sanitized derivatives require explicit approval |
| `llm-wiki` raw-like data | source inventories, extracted notes, staging packs, source cards, provenance metadata, RAG indexes | Private/local or controlled staging until reviewed |
| Public `llm-wiki` content | sanitized markdown pages and public chatbot/search corpus | Public-facing after source/legal/sanitization gates |
| Execution artifacts | issue plans, YAML/JSON configs, prompt bundles, tool manifests, run logs, checksums | Execution/report boundary; promote only manifests/evidence, not bulky generated data by default |
| Report artifacts | internal reports, client HTML, limited PDFs, chatbot/query configs/indexes | Report layer; audience-specific evidence and sanitization gates required |

### Concrete example path classes for user review
| Example path / pattern | Example contents | Data layer level | Public/private posture | Notes |
|---|---|---|---|---|
| `/mnt/ace/` raw PDFs → generated `.md` files | Standards/literature/project PDFs and their first-pass markdown extraction outputs | D-L1 raw/source data → D-L2 raw-like extraction output | Private/local source data | Treat the PDFs and unreviewed markdown as local/private source material; no direct public `llm-wiki` or client-report eligibility without promotion gates. |
| `[REDACTED-CLIENT-ROOT]` | Index files, markdown files, uncurated `llm-wiki` drafts/staging packs, extraction manifests | D-L2 raw-like structured/staging data | Private/local source data | Treat as staging and curation workspace; useful for source cards, inventories, RAG chunks, and reviewer work queues, but not public by default. |
| `/mnt/local-analysis/<repo>/` | repo checkouts such as `workspace-hub`, documented tier-1 engineering/data repos (`digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`), and knowledge/publication/strategy repos (`llm-wiki`, `aceengineer-website`, `aceengineer-strategy`) | D-L3 curated knowledge/data or repo-backed execution/report metadata, depending on repo/path | Public-facing only for explicitly public repos/content; sanitized/curated data only | Public `llm-wiki` content, curated data, and sanitized fixtures belong here when repo policy allows; private raw source data should not be inferred public just because it was used to create a sanitized derivative. |

### Client data handling model
Tracked public docs must not publish raw client-identifying path names. The implementation packet must use redacted source IDs in `docs/architecture/data-source-inventory.md` and keep any literal path mapping in a private-only appendix outside public docs, unless the source is explicitly public-safe.

| Source ID class | Runtime evidence posture | Allowed destination |
|---|---|---|
| `client_present_001`..`client_present_nnn` | verified-present private client/project roots from runtime probe; literal paths stay private | private staging or private client corpus only |
| `client_planned_001`..`client_planned_nnn` | planned/unavailable roots; not binding until provisioned and re-probed | follow-up issue before use |
| `client_llm_wiki_target` | `/mnt/local-analysis/<client>-llm-wiki` is a provisioning pattern, not an assumed existing repo | follow-up issue must create/private-register before implementation relies on it |
| `public_domain_source` | source/license/provenance/legal gates pass | public `llm-wiki` or public repo surface where policy allows |

Structured inventory source of truth for this packet is `tests/fixtures/architecture/data_source_inventory.yaml`; it must cross-link existing `data/document-index/mounted-source-registry.yaml` entries and must not fork that registry.

## Contract Logic
This is a documentation/architecture packet. Runtime classification code is out of scope unless a separate implementation issue is opened. Tests validate the machine-readable YAML fixtures, registry cross-links, redaction rules, and markdown views; they do not pretend to exercise a non-existent runtime function.

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
- [ ] Data source inventory includes concrete path-class examples for `/mnt/ace/` raw PDFs → markdown, `[REDACTED-CLIENT-ROOT]` private staging/indexes/uncurated wiki material, and `/mnt/local-analysis/<repo>/` repo-backed public-facing/curated surfaces, without assuming every local checkout is tier-1.
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
Do not summarize in-progress/current-cycle provider artifacts inside this plan body; `plan-review-fanout.sh` truncates target provider files before writing them, so self-referential artifact tables produce false 0-byte evidence findings.

Current gate: after this exact committed plan path is pushed, run `scripts/review/plan-review-fanout.sh <plan>` and inspect non-empty provider artifacts in `scripts/review/results/`. Gemini may be recorded as `UNAVAILABLE` during quota exhaustion, but Claude/Codex must return substantive artifacts and MAJOR findings must be cleared before any approval request.

---

## Risks and Open Questions
- **Risk:** Existing data residence tiers and proposed data-layer levels can be confused; implementation must use clear names and crosswalk table.
- **Risk:** Some `/mnt` inventories can expose client identifiers; tracked public docs must use redacted source IDs or private-only appendices for raw client path names.
- **Decision for this packet:** D-L2 raw-like `llm-wiki` staging is private/local only and registry-referenced; public `llm-wiki` private branches are not an approved storage home unless separately approved in a follow-up issue.
- **Open:** Which data sources should be considered chatbot-eligible by default after D-L3 promotion?

---

## Complexity: T3
Data governance crosses public/private repos, local mounts, client/project archives, llm-wiki, RAG/chatbot indexes, and legal/sanitization gates.
