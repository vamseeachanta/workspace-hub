# Plan for #2726: Review data, execution, and report layer boundaries

> **Status:** `status:plan-review` — revised after MAJOR review findings; pending re-review; not approved
> **Complexity:** T3
> **Date:** 2026-05-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2726
> **Review artifacts:** `scripts/review/results/2026-05-17-plan-2726-claude.md`, `scripts/review/results/2026-05-17-plan-2726-codex.md`, `scripts/review/results/2026-05-17-plan-2726-gemini.md`, `scripts/review/results/2026-05-17-plan-2726-disagreement.md`

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
- [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726) — issue body requests this architecture review and layer-specific scope.
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
| Mounted standards/literature | `/mnt/ace/docs/_standards`, `/mnt/ace/0000 O&G`, `/mnt/ace/acma-codes`, `/mnt/ace-data/digitalmodel/docs/domains`, `/mnt/ace/docs/literature/dde (migrated local copy; remote DDE archival)` | Reference-in-place; never blindly copy into public repos |
| Client/project data | `client_projects` / project repos / mounted project archives / local client folders | Private by default; sanitized derivatives only |
| `llm-wiki` raw-like data | source inventories, extracted notes, staging packs, source cards, provenance metadata, RAG indexes | Private/local or controlled staging until reviewed |
| Public `llm-wiki` content | sanitized markdown pages and public chatbot/search corpus | Public-facing after source/legal/sanitization gates |
| Execution artifacts | issue plans, YAML/JSON configs, prompt bundles, tool manifests, run logs, checksums | Execution/report boundary; promote only manifests/evidence, not bulky generated data by default |
| Report artifacts | internal reports, client HTML, limited PDFs, chatbot/query configs/indexes | Report layer; audience-specific evidence and sanitization gates required |

### Gaps identified
- No approved level taxonomy yet for A-DATA raw sources → private/raw-like staging → public-safe curated knowledge/publication surfaces.
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
| This plan | `docs/plans/2026-05-17-issue-2726-layer-boundary-architecture-review.md` |
| Data-layer child plan | `docs/plans/2026-05-17-issue-2727-data-layer-boundary-and-promotion.md` |
| Execution-layer child plan | `docs/plans/2026-05-17-issue-2728-execution-layer-contracts-routing.md` |
| Report-layer child plan | `docs/plans/2026-05-17-issue-2729-report-layer-outputs-evidence.md` |
| Target architecture contract | `docs/architecture/data-execution-report-layer-contract.md` |
| Source classification matrix | `docs/architecture/source-layer-classification-matrix.md` |
| Review artifacts | `scripts/review/results/2026-05-17-plan-2726-*.md` |
| Tests | `tests/governance/test_layer_boundary_architecture_contract.py` |
| Structured layer matrix fixture | `tests/fixtures/architecture/layer_boundary_matrix.yaml` |

---

## Deliverable
A reviewed architecture contract will define the repo ecosystem's **lifecycle** rather than a one-way layer stack:

```text
inputs → execution → reports/chatbots → curated output learnings → appropriate llm-wiki/corpus tier
```

The contract will define data, execution, report, and report-derived-learning boundaries; level taxonomy per layer; canonical source classes; promotion gates; output-residency rules; and ownership boundaries across `/mnt` data, client/project data, control-plane docs, public/private `llm-wiki`, execution machines, and report/chatbot surfaces.

### Final architecture decisions to encode
- **Data at rest remains separated by posture.** Raw/private/client data cannot be merged into public `llm-wiki`; public-safe domain knowledge may live in public `llm-wiki`; restricted/client/non-public derivatives route to private/domain/client corpora.
- **Execution owns manifests, not source truth.** Execution manifests reference data-layer `source_id`/path contracts and must carry both `input_residency` and `output_residency` metadata.
- **Reports are publication surfaces, not automatic knowledge promotion.** Raw outputs are internal evidence by default; client/public reports require evidence, legal/source checks, and sanitization.
- **Report-derived learnings are first-class.** Curated learnings from reports/chatbots route to public `llm-wiki`, domain-private corpus, or client-private `llm-wiki` only after the relevant promotion gate.
- **Canonical registries win.** Machine routing must use `config/workstations/registry.yaml`; mount/data location work must coordinate with #2731 and #2732; machine/provider routing must coordinate with #2119, #1838, and #2089.

---

## Pseudocode
```text
function build_layer_contract():
    inventory known source classes from tracked registries, repo docs, related issues, and user-added sources
    reconcile overlapping open issues (#2119, #1838, #2089, #2731, #2732) before creating new canonical surfaces
    assign each source class to a data/execution/report/report-derived-learning layer and level
    define allowed lifecycle transitions: inputs -> execution -> reports/chatbots -> curated output learnings -> corpus tier
    define required gates for each transition: provenance, license/legal, sanitization, tests, review, output_residency
    define canonical owner repo/path and fallback behavior for unavailable mounts
    define report/chatbot eligibility rules from data classification, execution evidence, and output residency
    publish architecture contract plus source matrix plus follow-up issue backlog
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/data-execution-report-layer-contract.md` | Main architecture contract |
| Create | `docs/architecture/source-layer-classification-matrix.md` | Reviewable initial source inventory and level assignment |
| Update | `docs/DATA_RESIDENCE_POLICY.md` | Cross-link expanded architecture; do not replace existing policy without review |
| Update | `docs/content-pipeline/README.md` | Align publication/report-layer language if approved |
| Update | `docs/plans/2026-05-17-issue-2727-data-layer-boundary-and-promotion.md` | Keep data-layer child plan aligned with parent contract |
| Update | `docs/plans/2026-05-17-issue-2728-execution-layer-contracts-routing.md` | Keep execution-layer child plan aligned with parent contract |
| Update | `docs/plans/2026-05-17-issue-2729-report-layer-outputs-evidence.md` | Keep report-layer child plan aligned with parent contract |

---

## TDD / Validation List
| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_source_matrix_has_required_columns | Source matrix fixture has source_class, owner, canonical_path, layer, level, allowed_artifacts, forbidden_artifacts, retention_expectations, publication_rules, public_posture, promotion_gate, output_residency, report_chatbot_eligibility | `tests/fixtures/architecture/layer_boundary_matrix.yaml` | all required columns present |
| test_private_sources_not_public_eligible_by_default | Client/mounted/private roots cannot map directly to public `llm-wiki` or client report without gates | source matrix | violations fail |
| test_layer_transitions_are_explicit | Every lifecycle path names required gates, including report-derived-learning routing | layer contract | no implicit promotion paths |
| test_known_sources_are_classified | Initial known sources from this plan are represented | source matrix | all seed classes present |
| test_legal_scan_passes | Contract and matrix avoid client identifiers/secrets | plan/docs paths | legal sanity scan passes |

---

## Acceptance Criteria
- [ ] Child plans for [#2727](https://github.com/vamseeachanta/workspace-hub/issues/2727), [#2728](https://github.com/vamseeachanta/workspace-hub/issues/2728), and [#2729](https://github.com/vamseeachanta/workspace-hub/issues/2729) are source-curated and reviewed.
- [ ] Architecture contract defines level taxonomy for data, execution, and report layers.
- [ ] Initial known source classes distinguish control-plane repo data, documented tier-1 repos, tier-2/publication repos, public/private `llm-wiki`, execution artifacts, and report/chatbot artifacts; it must not mislabel `workspace-hub`, `llm-wiki`, `aceengineer-website`, or `aceengineer-strategy` as tier-1 unless the cited registry says so.
- [ ] Matrix defines owner repo/path, public/private posture, promotion gate, output_residency, and report/chatbot eligibility for each source class.
- [ ] Legal/security scan passes for all created docs.
- [ ] Re-review artifacts are substantive for Claude/Codex, Gemini is substantive or explicitly UNAVAILABLE due quota, and no unresolved MAJOR findings remain before asking the user for approval.
- [ ] No implementation or publication changes occur before user approval.

---

## Adversarial Review Summary
Do not summarize in-progress/current-cycle provider artifacts inside this plan body; `plan-review-fanout.sh` truncates target provider files before writing them, so self-referential artifact tables produce false 0-byte evidence findings.

Current gate: after this exact committed plan path is pushed, run `scripts/review/plan-review-fanout.sh <plan>` and inspect non-empty provider artifacts in `scripts/review/results/`. Gemini may be recorded as `UNAVAILABLE` during quota exhaustion, but Claude/Codex must return substantive artifacts and MAJOR findings must be cleared before any approval request.

---

## Risks and Open Questions
- **Decision:** Use architecture-surface IDs `A-DATA`, `A-EXEC`, `A-REPORT`, and `A-CURATED-LEARNING` in parent docs; child D-/R- codes must include a crosswalk to existing document-intelligence L-levels and must not redefine normative L1/L2/L3/L5 semantics.
- **Risk:** Mounted project/source paths can contain sensitive client names; inventories must support redaction and source IDs.
- **Open:** Should execution input data be classified primarily under data layer, execution layer, or both via an input-contract boundary?
- **Open:** Which repo is canonical for private `llm-wiki` raw/staging content if not the public `llm-wiki` repo?

---

## Complexity: T3
Multi-repo, multi-layer architecture/governance issue with sensitive-data, public/private publication, compute-routing, and chatbot/reporting implications.
