# Plan for #2729: Define report layer outputs, publication surfaces, and evidence rules

> **Status:** `status:plan-approved` — user approved on 2026-05-18; implementation authorized
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2729
> **Review artifacts:** prior-cycle blockers are summarized in `scripts/review/results/2026-05-17-plan-2729-disagreement.md`; current-cycle Claude/Codex/Gemini artifacts must be generated after this revision and verified non-empty before an approval request. Do not cite same-cycle per-provider paths from this plan body.

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
- [#2729](https://github.com/vamseeachanta/workspace-hub/issues/2729) — issue body requests this architecture review and layer-specific scope.
- [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726) — parent architecture issue for data, execution, and report layer boundaries.
- [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209) — durable-vs-transient knowledge boundary and publication governance reference.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — control-plane/reporting boundary reference.
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
- Parent/data/execution taxonomy remains in `status:plan-review`; this report plan must consume #2726/#2727/#2728 only after those plans clear MAJOR findings, or fail closed to local schema fields defined here without inventing upstream interfaces.
- No approved level taxonomy yet for execution inputs vs data-layer inputs, code/tooling, machines/compute, validation evidence, and handoff manifests.
- No approved level taxonomy yet for report raw outputs, data outputs, HTML/PDF/report formats, interactivity, and chatbot surfaces.
- No canonical matrix yet mapping source class → owner repo/path → public/private posture → promotion gate → report/chatbot eligibility.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-17T01:12:21Z via `gh issue view`):
- `#2729` — OPEN — feat(architecture): define report layer outputs, publication surfaces, and evidence rules
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
data/document-index/registry.yaml and resource-intelligence-maturity.yaml — registry/maturity data is source-of-truth for document-index provenance and readiness; architecture contracts must link rather than fork these registries and must record unavailable source families explicitly.
Cross-repo report-surface inventory sample (2026-05-17): `git -C /mnt/local-analysis/llm-wiki ls-tree -r --name-only HEAD | grep -Ei '(report|html|pdf|chatbot|dashboard|gtm|demo)' | head` found `docs/reports/*` and conversion-oracle HTML fixtures; `/mnt/local-analysis/digitalmodel` found benchmark HTML/report JSON/report generators under `docs/benchmarks/` and `docs/domains/orcaflex/`; `/mnt/local-analysis/aceengineer-website` and `/mnt/local-analysis/aceengineer-strategy` were not present in this runtime and must be inventoried from another machine or marked unavailable before closeout.
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
| This plan | `docs/plans/2026-05-17-issue-2729-report-layer-outputs-evidence.md` |
| Report layer contract | `docs/architecture/report-layer-contract.md` |
| Report output taxonomy | `docs/architecture/report-output-taxonomy.md` |
| Publication/evidence gates | `docs/architecture/report-publication-gates.md` |
| Evidence bundle schema | `docs/architecture/report-evidence-bundle-schema.md` and `docs/architecture/report-evidence-bundle.schema.yaml` |
| Report-derived learning routing | `docs/architecture/report-derived-learning-routing.md` |
| Follow-up issue backlog | `docs/architecture/report-follow-up-issue-backlog.md` |
| Tests | `tests/architecture/test_report_layer_contract.py`; fixtures in `tests/fixtures/architecture/report_evidence_bundle.yaml` and `tests/fixtures/architecture/report_residency_cases.yaml` |
| Prior-cycle review synthesis | `scripts/review/results/2026-05-17-plan-2729-disagreement.md` |

---

## Deliverable
A report-layer contract will classify raw outputs, evidence bundles, client/internal/public reports, HTML/PDF formats, interactivity, chatbot/query surfaces, and **report-derived knowledge**. It will add `output_residency` as a required classification field and define where curated learnings from reports/chatbots are preserved: public `llm-wiki` for public-safe domain knowledge, domain-private corpus for restricted/non-public derivatives, and registered client-private corpus for client-derived learnings. `/mnt/local-analysis/<client>-llm-wiki` is a provisioning pattern only, not an approved destination until a private repo/corpus registry issue creates and verifies it. Raw generated outputs remain internal by default.

This child issue is separately dispatchable because it owns publication/output/evidence rules, but every R-layer promotion must consume data residency from #2727 and execution evidence from #2728 through the parent #2726 lifecycle contract.

---

## Proposed Report Layer Levels
| Level | Working name | Contents | Audience/posture |
|---|---|---|---|
| R-L1 | Raw execution outputs | generated CSV/JSON, plots, screenshots, logs, model outputs, intermediate HTML | Internal evidence only; not a deliverable by default |
| R-L2 | Evidence bundles | source manifests, command manifests, checksums, validation outputs, legal scans, review verdicts | Internal/review; public-safe excerpts allowed |
| R-L3 | Internal decision reports | audit reports, plan reviews, kanban dashboards, readiness reports, technical review HTML/MD | Internal repo governance; evidence-bounded |
| R-L4 | Client/public deliverables | polished client-facing HTML, limited PDFs, public website pages, sanitized demos | Public/client only after evidence/legal/source/sanitization gates |
| R-L5 | Interactive/query surfaces | chatbots, RAG/search UIs, dashboards, API/query surfaces, embedded notebooks | Must inherit data-corpus posture via manifest field/check and disclose evidence/freshness limits |
| R-L6 | Curated report-derived learnings | distilled reusable insights, sanitized methodology notes, source-backed corrections, client-specific learnings | Route by `output_residency`: public `llm-wiki`, domain-private corpus, or client-private `llm-wiki`; never preserve raw/private details in public corpus |

---

## Pseudocode
```text
function classify_report_artifact(artifact):
    identify source execution manifest and data source classification
    assign report level R-L1..R-L6, including curated report-derived learning artifacts
    require evidence bundle for R-L3+ and publication gates for R-L4/R-L5
    require output_residency for R-L2+ and for all report-derived learnings
    validate public/client artifact with canonical legal scan plus source/legal/sanitization checklist
    select output format: HTML-first, PDF only when required, chatbot/index only when corpus posture allows
    route curated report-derived learnings to public, domain-private, registered client-private corpus, ignored-internal, or no-preserve according to output_residency
    record freshness, limitations, and provenance links
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/report-layer-contract.md` | Defines report layer levels and boundaries |
| Create | `docs/architecture/report-output-taxonomy.md` | Maps artifact types to R-level, owner, storage posture, and audience |
| Create | `docs/architecture/report-publication-gates.md` | Defines evidence/legal/sanitization gates for HTML/PDF/chatbot/public surfaces and wraps/reuses `scripts/legal/legal-sanity-scan.sh` / `.legal-deny-list.yaml` rather than inventing a parallel denylist |
| Create | `docs/architecture/report-evidence-bundle-schema.md` | Human-readable evidence bundle contract |
| Create | `docs/architecture/report-evidence-bundle.schema.yaml` | Machine-readable schema source for `output_residency`, claim binding, and evidence requirements |
| Create | `docs/architecture/report-derived-learning-routing.md` | Defines public/domain-private/client-private destinations for report-derived knowledge |
| Create | `docs/architecture/report-follow-up-issue-backlog.md` | Exact `gh issue create --title ... --body-file ... --label ...` command blocks and body drafts for report validators, artifact indexes, and publication pipelines; if not filed immediately, blocker reason is recorded |
| Create | `tests/fixtures/architecture/report_evidence_bundle.yaml` | Evidence bundle fixture covering claim-to-source/command/validation/legal/checksum/review binding |
| Create | `tests/fixtures/architecture/report_residency_cases.yaml` | Residency/publication routing fixture cases |
| Create | `tests/fixtures/architecture/report_output_taxonomy.yaml` | Seed artifact taxonomy fixture for raw outputs, HTML/PDF, chatbot/query, public page, and report-derived learning cases |
| Create | `tests/architecture/test_report_layer_contract.py` | Tests taxonomy/manifest fixtures and posture invariants, not only markdown phrase presence |
| Update | `docs/content-pipeline/README.md` | Add a bounded cross-link to report publication/routing rules after approval; no broad rewrite in this issue |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_raw_outputs_not_deliverables_by_default | R-L1 fixture cannot be promoted to client/public deliverable without evidence and output_residency | taxonomy fixtures | invalid promotion fails |
| test_html_default_pdf_limited | Output policy fixture permits HTML by default and requires exception reason for PDF | taxonomy fixtures | PDF without reason fails |
| test_client_public_requires_evidence_bundle | R-L4/R-L5 fixture requires evidence/legal/sanitization gates and canonical legal scan reference | evidence bundle fixture | missing gate fails |
| test_chatbot_inherits_corpus_posture | Chatbot/query surface cannot be more public than underlying data corpus | corpus/report manifest fixtures | public chatbot over private corpus fails |
| test_report_derived_learning_routes_by_output_residency | Curated learnings route to public `llm-wiki`, domain-private, or client-private corpus based on output_residency | routing fixtures | wrong destination fails |
| test_report_taxonomy_seed_artifacts | Raw outputs, evidence bundles, internal reports, client HTML, PDFs, chatbots, public pages, and report-derived learnings are represented | taxonomy | all seed artifact types present |
| test_evidence_bundle_claim_binding | Each published claim binds to source manifest, command manifest, validation result, legal scan, checksum, review verdict, output_residency, and promotion decision | evidence bundle schema + fixture | missing or unbound claim evidence fails |
| test_follow_up_issue_backlog_present | Validators/artifact-index/publication-pipeline gaps have exact `gh issue create` command/body drafts or explicit no-action/blocker rationale | backlog | every gap accounted for |

---

## Acceptance Criteria
- [ ] Report levels R-L1 through R-L6 are defined, including report-derived knowledge.
- [ ] Raw outputs are explicitly not deliverables by default.
- [ ] HTML is default for rich human-facing reports; PDFs are limited/exported only when needed.
- [ ] Client/public reports require data provenance, execution evidence, legal/source checks, and sanitization.
- [ ] Chatbots/query surfaces inherit underlying data-corpus public/private posture and freshness limitations through explicit manifest fields/tests, not prose-only policy.
- [ ] Output taxonomy includes raw outputs, evidence bundles, internal reports, client-facing HTML, limited PDFs, dashboards/interactivity, public website content, chatbots, and report-derived learnings.
- [ ] `output_residency` is defined once in `docs/architecture/report-evidence-bundle.schema.yaml` with enum values `public_llm_wiki`, `domain_private_corpus`, `registered_client_private_corpus`, `ignored_internal_run_artifact`, and `no_preserve`; each enum value has a `registry_backing` rule in the schema (`public_llm_wiki` requires the public repo/corpus row, `domain_private_corpus` and `registered_client_private_corpus` require registered private corpus rows, internal/no-preserve values require evidence-only retention), and unregistered `/mnt/local-analysis/<client>-llm-wiki` paths fail closed with a follow-up issue body path.
- [ ] Evidence bundle schema is concrete and falsifiably tested: each published claim binds to source manifest, command manifest, validation, legal scan, checksums, and review verdicts.
- [ ] Cross-repo report inventory covers workspace-hub, llm-wiki, digitalmodel, aceengineer-website, and aceengineer-strategy, or records unavailable evidence with command, machine, timestamp, and reason.
- [ ] R-L6 report-derived learning routing explicitly references #2209 and `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`; it is a crosswalk onto the existing durable/transient boundary, not a new competing intelligence layer, and durable learnings are separated from transient/raw outputs.
- [ ] Follow-up implementation work is represented by exact `gh issue create` command/body drafts in `docs/architecture/report-follow-up-issue-backlog.md`; no implementation is embedded in this plan.
- [ ] Verification commands are explicit and must pass after implementation: `uv run pytest tests/architecture/test_report_layer_contract.py -v` and `git add -N <new-files> && scripts/legal/legal-sanity-scan.sh --diff-only`.
- [ ] Revised plan receives substantive Claude/Codex re-review before approval request; Gemini must be substantive or explicitly `UNAVAILABLE` due quota, and no unresolved MAJOR findings may remain.

---

## Revision / Adversarial Review Summary

Prior-cycle MAJOR disposition for this revision:

| Finding class | Disposition in this revision |
|---|---|
| Invented client-private destination | Reframed `/mnt/local-analysis/<client>-llm-wiki` as unapproved provisioning pattern; only registered private client corpus is valid. |
| Fixture map incomplete | Added explicit Files-to-Change rows for every fixture referenced by tests. |
| `output_residency` schema missing | Added machine-readable schema artifact and enum/fail-closed AC. |
| Cross-repo inventory partial | Added inventory fixture/TDD/AC requiring complete coverage or explicit unavailable evidence. |
| R-L6 policy collision | Added explicit reconciliation with #2209 and durable-vs-transient knowledge boundary. |
| Evidence claim binding untested | Added `test_evidence_bundle_claim_binding`. |
| Follow-up issues weakened | Follow-up bundle now requires exact `gh issue create` commands/body drafts. |

Do not summarize in-progress/current-cycle provider artifacts inside this plan body; `plan-review-fanout.sh` truncates target provider files before writing them, so self-referential artifact tables produce false 0-byte evidence findings.

Current gate: after this exact committed plan path is pushed, run `scripts/review/plan-review-fanout.sh <plan>` and inspect non-empty provider artifacts in `scripts/review/results/`. Gemini may be recorded as `UNAVAILABLE` during quota exhaustion, but Claude/Codex must return substantive artifacts and MAJOR findings must be cleared before any approval request.

---

## Risks and Open Questions
- **Risk:** Generated reports may contain private paths or client names; report gates need automated and manual checks.
- **Risk:** Chatbot/RAG surfaces can silently expose lower-level data; corpus posture inheritance is mandatory.
- **Decision:** PDFs are durable deliverables only when a contract/client/regulatory/export requirement is recorded in the report taxonomy row; otherwise PDFs are transient exports derived from HTML-first reports and inherit R-L1/R-L2 internal evidence posture unless separately promoted.
- **Decision:** Report artifact ownership is selected by audience and source posture: `workspace-hub` holds governance/evidence contracts and internal review outputs; project/client repos hold client-specific deliverables and private evidence; `aceengineer-website` holds sanitized public demos/pages; public `llm-wiki` holds only curated public-safe report-derived knowledge. Ambiguous artifacts fail closed to internal evidence until the taxonomy row records an owner and output_residency; ambiguous artifacts fail closed is a tested contract requirement, not guidance.

---

## Complexity: T3
Report architecture crosses internal evidence, client/public publication, HTML/PDF generation, interactive dashboards, chatbots/RAG, and legal/sanitization boundaries.
