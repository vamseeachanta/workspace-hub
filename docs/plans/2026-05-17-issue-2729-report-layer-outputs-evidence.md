# Plan for #2729: Define report layer outputs, publication surfaces, and evidence rules

> **Status:** `status:plan-review` — re-reviewed 2026-05-17; awaiting user decision; not approved
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2729
> **Review artifacts:** `scripts/review/results/2026-05-17-plan-2729-claude.md`, `scripts/review/results/2026-05-17-plan-2729-codex.md`, `scripts/review/results/2026-05-17-plan-2729-gemini.md`, `scripts/review/results/2026-05-17-plan-2729-disagreement.md`

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
- [#2729](https://github.com/vamseeachanta/workspace-hub/issues/2729) — issue body requests this architecture review and layer-specific scope.
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
- `#2729` — OPEN — feat(architecture): define report layer outputs, publication surfaces, and evidence rules
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
| This plan | `docs/plans/2026-05-17-issue-2729-report-layer-outputs-evidence.md` |
| Report layer contract | `docs/architecture/report-layer-contract.md` |
| Report output taxonomy | `docs/architecture/report-output-taxonomy.md` |
| Publication/evidence gates | `docs/architecture/report-publication-gates.md` |
| Tests | `tests/architecture/test_report_layer_contract.py` |
| Review artifacts | `scripts/review/results/2026-05-17-plan-2729-*.md` |

---

## Deliverable
A report-layer contract will classify raw outputs, data outputs, client/internal/public reports, HTML/PDF formats, interactivity, and chatbot/query surfaces, with evidence and sanitization gates before publication.

---

## Proposed Report Layer Levels
| Level | Working name | Contents | Audience/posture |
|---|---|---|---|
| R-L1 | Raw execution outputs | generated CSV/JSON, plots, screenshots, logs, model outputs, intermediate HTML | Internal evidence only; not a deliverable by default |
| R-L2 | Evidence bundles | source manifests, command manifests, checksums, validation outputs, legal scans, review verdicts | Internal/review; public-safe excerpts allowed |
| R-L3 | Internal decision reports | audit reports, plan reviews, kanban dashboards, readiness reports, technical review HTML/MD | Internal repo governance; evidence-bounded |
| R-L4 | Client/public deliverables | polished client-facing HTML, limited PDFs, public website pages, sanitized demos | Public/client only after evidence/legal/source/sanitization gates |
| R-L5 | Interactive/query surfaces | chatbots, RAG/search UIs, dashboards, API/query surfaces, embedded notebooks | Must inherit data-corpus posture and disclose evidence/freshness limits |

---

## Pseudocode
```text
function classify_report_artifact(artifact):
    identify source execution manifest and data source classification
    assign report level R-L1..R-L5
    require evidence bundle for R-L3+ and publication gates for R-L4/R-L5
    validate public/client artifact has no private paths, client identifiers, or unsupported claims
    select output format: HTML-first, PDF only when required, chatbot/index only when corpus posture allows
    record freshness, limitations, and provenance links
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/report-layer-contract.md` | Defines report layer levels and boundaries |
| Create | `docs/architecture/report-output-taxonomy.md` | Maps artifact types to R-level, owner, storage posture, and audience |
| Create | `docs/architecture/report-publication-gates.md` | Defines evidence/legal/sanitization gates for HTML/PDF/chatbot/public surfaces |
| Create | `tests/architecture/test_report_layer_contract.py` | Guards HTML default, PDF limits, chatbot corpus posture, evidence requirements |
| Update | `docs/content-pipeline/README.md` | Cross-link publication/report rules after approval |
| Update | `docs/plans/README.md` | Plan index entry |

---

## TDD Test List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_raw_outputs_not_deliverables_by_default | R-L1 cannot be treated as client/public deliverable | report contract | explicit prohibition present |
| test_html_default_pdf_limited | Contract uses HTML-first and PDF-limited posture | report contract | HTML default and PDF exceptions present |
| test_client_public_requires_evidence_bundle | R-L4/R-L5 require evidence/legal/sanitization gates | publication gates | required gates present |
| test_chatbot_inherits_corpus_posture | Chatbot/query surface cannot be more public than underlying data corpus | taxonomy | inheritance rule present |
| test_report_taxonomy_seed_artifacts | Raw outputs, evidence bundles, internal reports, client HTML, PDFs, chatbots, public pages are represented | taxonomy | all seed artifact types present |

---

## Acceptance Criteria
- [ ] Report levels R-L1 through R-L5 are defined.
- [ ] Raw outputs are explicitly not deliverables by default.
- [ ] HTML is default for rich human-facing reports; PDFs are limited/exported only when needed.
- [ ] Client/public reports require data provenance, execution evidence, legal/source checks, and sanitization.
- [ ] Chatbots/query surfaces inherit underlying data-corpus public/private posture and freshness limitations.
- [ ] Output taxonomy includes raw outputs, evidence bundles, internal reports, client-facing HTML, limited PDFs, dashboards/interactivity, public website content, and chatbots.
- [ ] Validation tests and legal scan are planned before implementation.
- [ ] Plan receives adversarial review before `status:plan-review`.

---

## Adversarial Review Summary
Re-reviewed on 2026-05-17 with Claude, Codex, and Gemini via `scripts/review/plan-review-fanout.sh`.

| Provider | Artifact | Verdict |
|---|---|---|
| Claude | `scripts/review/results/2026-05-17-plan-2729-claude.md` | MAJOR |
| Codex | `scripts/review/results/2026-05-17-plan-2729-codex.md` | MAJOR |
| Gemini | `scripts/review/results/2026-05-17-plan-2729-gemini.md` | MAJOR |
| Disagreement report | `scripts/review/results/2026-05-17-plan-2729-disagreement.md` | MAJOR findings consolidated |

Plan is in `status:plan-review` for user review only. Do not implement or mark `status:plan-approved` until the user explicitly approves a revised plan.

---

## Risks and Open Questions
- **Risk:** Generated reports may contain private paths or client names; report gates need automated and manual checks.
- **Risk:** Chatbot/RAG surfaces can silently expose lower-level data; corpus posture inheritance is mandatory.
- **Open:** Which PDFs are legitimate durable deliverables versus transient exports?
- **Open:** Which report artifacts belong in project/client repos versus `workspace-hub` governance docs versus website repos?

---

## Complexity: T3
Report architecture crosses internal evidence, client/public publication, HTML/PDF generation, interactive dashboards, chatbots/RAG, and legal/sanitization boundaries.
