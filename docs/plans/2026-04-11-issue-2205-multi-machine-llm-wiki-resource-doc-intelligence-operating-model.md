# Plan for #2205: multi-machine llm-wiki + resource/document intelligence operating model

> Status: draft
> Complexity: T3
> Date: 2026-04-11
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2205
> Review artifacts: scripts/review/results/2026-04-11-plan-2205-claude.md | scripts/review/results/2026-04-11-plan-2205-codex.md | scripts/review/results/2026-04-11-plan-2205-gemini.md

---

## Resource Intelligence Summary

### Existing repo code / artifacts
- Found: `knowledge/wikis/engineering/wiki/index.md` and `knowledge/wikis/engineering/wiki/entities/llm-wiki-tool.md` confirm active repo-tracked llm-wiki assets already exist under `knowledge/wikis/`.
- Found: `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` already defines weekly questions around freshness, accessibility, canonical entry points, and machine reachability.
- Found: `docs/assessments/document-intelligence-audit.md` documents a 7-phase document-intelligence pipeline, `data/document-index/registry.yaml`, and a standards transfer ledger with broad corpus coverage.
- Found: `docs/document-intelligence/holistic-resource-intelligence.md` already frames a multi-source resource registry architecture spanning `/mnt/ace`, mounted drives, online registries, and pipeline outputs.
- Found: planning governance already exists in `docs/plans/README.md`, `docs/plans/_template-issue-plan.md`, and `.claude/skills/coordination/issue-planning-mode/SKILL.md`.

### Standards / registries / implementation surfaces
- Found likely cross-machine and provenance surfaces called out by architecture review:
  - `data/document-index/registry.yaml`
  - `data/document-index/standards-transfer-ledger.yaml`
  - `data/document-index/mounted-source-registry.yaml`
  - `config/workstations/registry.yaml`
  - `scripts/data/document-index/provenance.py`
  - `scripts/data/document-index/phase-e-registry.py`
  - `scripts/data/document-index/query-ledger.py`
  - `scripts/data/doc_intelligence/query.py`
  - `scripts/knowledge/llm_wiki.py`
- Gap: there is no single parent architecture document that defines how these layers relate, which layer owns what, and how information should flow without duplicate parsing or duplicate tracking.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md`
- `knowledge/wikis/engineering/wiki/entities/llm-wiki-tool.md`

### Documents consulted
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/assessments/document-intelligence-audit.md`
- `docs/document-intelligence/holistic-resource-intelligence.md`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`

### Related prior work
- Existing related issues already cover parts of the scope:
  - `#2089` weekly ecosystem execution/intelligence review
  - `#2096` intelligence accessibility map
  - `#2104` canonical entry points for ecosystem intelligence
  - `#2136` intelligence accessibility registry with machine reachability metadata
  - `#2034` engineering LLM wiki seed + incremental ingest pipeline
  - `#1563` consolidated data/resource intelligence feature
  - `#1575` holistic document/resource intelligence architecture
- New follow-on child issues created during planning to isolate the missing contracts and downstream validation:
  - `#2206` conformance checks for the approved single-source-of-truth pyramid
  - `#2207` standards/codes provenance + reuse contract for llm-wiki promotion
  - `#2208` intelligence retrieval contract for issue planning/execution/review
  - `#2209` durable-vs-transient knowledge boundary policy

### Gaps identified
- No canonical single-source-of-truth pyramid currently defines the layers from raw documents to execution state.
- No explicit contract defines when llm-wikis should consume existing document-intelligence outputs versus reparsing raw documents.
- No strict retrieval-evidence contract currently forces future issue plans to prove they consulted the relevant wiki/registry/issue artifacts.
- No explicit boundary policy cleanly separates durable wiki knowledge, GitHub execution state, registries, and transient session artifacts.

### Scope split
- In scope now (`#2205`): define the parent operating model, issue tree, dependency order, and scope boundaries so detailed implementation can proceed without overlap.
- Child implementation/design scope (not absorbed into `#2205`):
  - `#2096` accessibility inventory/map
  - `#2104` canonical entry points
  - `#2136` machine-readable accessibility registry
  - `#2206` conformance checks against the approved parent model
  - `#2207` provenance + reuse contract
  - `#2208` workflow retrieval contract
  - `#2209` durable/transient boundary policy

### Risks / unknowns
- Risk: parent issue drifts into re-implementing child scopes unless boundaries are explicit in the deliverable.
- Risk: cross-machine storage/query assumptions are partially documented but not yet normalized around one canonical doc identity.
- Decision to lock in at parent level: `#2205` will require a unified artifact-registry concept as an architectural requirement only, while exact schema/file ownership remains delegated to `#2207` and `#2136`.

### Artifact map
| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` |
| Parent operating-model doc | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` |
| Plan review — Claude | `scripts/review/results/2026-04-11-plan-2205-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-11-plan-2205-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-11-plan-2205-gemini.md` |
| Planning index update | `docs/plans/README.md` |
| Parent issue thread | GitHub issue `#2205` |

---

## Deliverable

A repo-tracked parent architecture/operating-model document plus linked GitHub issue tree that defines the single-source-of-truth pyramid, cross-machine information-flow rules, scope boundaries, and dependency order for llm-wikis, resource intelligence, document intelligence, and issue workflows.

---

## Parent architecture decisions to lock in

### Canonical document identity rule
- Canonical `doc_key` is content-based (`sha256` / content hash) rather than path-based.
- File paths, mount-specific locations, and cache copies are aliases/locations of the same document when they resolve to the same `doc_key`.
- Registries, manifests, summaries, promoted artifacts, and wiki-ready records must refer upward to the same `doc_key` instead of inventing separate identities.
- Path is still retained for provenance and reachability, but path never outranks content identity as the source of truth.

### Single-source-of-truth pyramid owner map
| Layer | Owns | Must not own | Primary artifact examples |
|---|---|---|---|
| Source documents | raw external/source files and original locations | promoted summaries, workflow state, narrative synthesis | mounted sources, `/mnt/ace`, external docs |
| Registry/provenance layer | inventory, hashes, paths, lineage, availability, extraction status | durable narrative knowledge, issue state | `data/document-index/*.yaml`, manifests, ledgers |
| Durable knowledge layer | distilled reusable knowledge and conceptual synthesis | live execution state, source-of-truth provenance | `knowledge/wikis/**` |
| Entry-point layer | human/agent navigation surfaces into the intelligence system | raw source inventory, execution state | `#2096`, `#2104`, docs entry points |
| Execution-state layer | scope, owner, approval state, acceptance criteria, delivery tracking | durable technical knowledge, provenance truth | GitHub issues/plans/reviews |
| Transient session layer | handoffs, research notes, working context, temporary synthesis candidates | canonical durable knowledge, canonical execution state | `.planning/`, handoffs, session artifacts |

### Allowed / forbidden information flows
Allowed flows:
- source documents -> registry/provenance artifacts
- registry/provenance artifacts -> durable knowledge promotion
- registry/provenance artifacts -> entry-point/index surfaces
- durable knowledge + registry/provenance artifacts -> issue planning/execution/review consumption
- transient session artifacts -> durable knowledge promotion only after explicit promotion decision
- execution-state artifacts -> durable knowledge only through post-issue promotion, never by becoming the durable store themselves

Forbidden flows:
- llm-wikis reparsing raw documents when sufficient registry/promoted evidence already exists
- GitHub issues acting as the durable knowledge base
- transient session artifacts becoming canonical source of truth without promotion
- entry-point docs inventing new provenance facts not backed by registry/provenance layer
- path-only identity creating duplicate truth for the same content across machines

Named exceptions:
- audit/provenance lookbacks may read across layers to verify lineage
- degraded/offline mode may consume cached registry evidence when the raw source is unreachable, but must preserve the canonical `doc_key` and mark availability state

### Degraded / offline fallback policy
- Git-tracked metadata remains the minimal cross-machine truth when shared mounts/artifact stores are unavailable.
- Shared derived artifacts are preferred for summaries/extractions/promoted outputs when reachable.
- Local caches are performance layers only; they may serve read-through copies but must not silently become canonical without explicit promotion.

### Unified artifact registry decision
- `#2205` will require a unified artifact-registry concept at the architecture level: one lookup model that can map `doc_key` to source refs, summaries, manifests, promoted artifacts, wiki refs, and issue/workflow refs.
- `#2205` will not define the concrete schema or implementation location for that registry; those details remain delegated to `#2207` and `#2136`.

## Pseudocode

```text
collect existing related issues and intelligence docs
lock canonical doc identity to content hash/doc_key with path aliases below it
classify each artifact as source, registry/provenance, durable knowledge, entry-point, execution-state, or transient
assign one canonical owner per layer and forbid overlapping ownership
enumerate allowed flows, forbidden flows, and explicit audit/degraded-mode exceptions
state multi-machine access model: git metadata + shared derived artifacts + local cache
classify related issues as inputs, children, or downstream consumers
state what each child may implement and must not redefine
publish parent operating-model doc and issue-tree summary
```

---

## Related issue classification and child guardrails

| Issue | Classification | Role in #2205 | Must not redefine |
|---|---|---|---|
| `#2034` | input / upstream producer | existing llm-wiki ingest/seed capability | parent pyramid ownership model |
| `#1563` | input / upstream program | broader data/resource-intelligence umbrella | #2205 architectural boundaries |
| `#1575` | input / upstream architecture | multi-source resource-intelligence framing | parent layer ownership and issue-workflow policy |
| `#2096` | child implementation | accessibility inventory/map | canonical layer ownership, doc identity, or workflow policy |
| `#2104` | child implementation | canonical entry-point design | provenance ownership or execution-state policy |
| `#2136` | child implementation | machine-readable accessibility registry | parent pyramid contract or durable/transient boundary |
| `#2206` | child validation | conformance checks against approved model | the pyramid itself |
| `#2207` | child contract | provenance + reuse details under approved model | parent ownership model or issue-workflow policy |
| `#2208` | child workflow contract | retrieval evidence and workflow enforcement | provenance schema or pyramid ownership |
| `#2209` | child policy | durable-vs-transient boundary details | provenance schema or accessibility registry design |
| `#2089` | downstream consumer | weekly verification/health checks against approved model | parent architectural source of truth |

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | parent operating-model document for #2205 in an existing intelligence-docs surface |
| Update | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` | fill review summary / revisions during planning |
| Update | `docs/plans/README.md` | add plan index row for #2205 |
| Update | GitHub issue `#2205` | post planning notes, issue tree, and final plan-review comment |
| Create | GitHub issues `#2206`, `#2207`, `#2208`, `#2209` | capture out-of-scope detailed follow-on work discovered during planning |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_parent_doc_defines_all_pyramid_layers | parent doc names each layer and its owner | draft operating-model doc | explicit layer list with ownership boundaries |
| test_parent_doc_links_existing_and_new_child_issues | parent doc references all reused and newly created child issues and classifies them | draft operating-model doc + issue tree | complete linked dependency map with input/child/consumer roles |
| test_scope_boundaries_prevent_duplicate_ownership | parent doc clearly separates parent scope from child scopes | scope section | no child implementation detail absorbed into parent deliverable |
| test_information_flow_rules_are_directional | flow model avoids circular or competing source-of-truth claims while allowing explicit audit/provenance exceptions | flow section | explicit allowed/forbidden flows and named exceptions |
| test_cross_machine_model_is_explicit | parent doc states git metadata vs shared derived artifacts vs local cache roles | storage/access section | clear multi-machine access model |
| test_canonical_identity_and_degraded_mode_are_defined | parent doc defines canonical document identity and offline/degraded behavior expectations | identity + degraded-mode sections | explicit doc-key rule and fallback semantics |
| test_doc_location_is_canonical_and_discoverable | chosen doc path is justified and cross-linked from existing intelligence docs/issues | doc-location section | rationale plus discoverability links |

---

## Acceptance Criteria

- [ ] Parent operating-model doc exists at `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- [ ] Parent doc defines the single-source-of-truth pyramid and assigns one owner per layer
- [ ] Parent doc defines allowed information flow across layers, including named audit/provenance exceptions and multi-machine behavior
- [ ] Parent doc defines canonical document identity expectations and degraded/offline fallback behavior
- [ ] Parent doc explicitly states what stays in `#2205` versus what is delegated to child issues
- [ ] Existing related issues (`#2096`, `#2104`, `#2136`, `#2089`, `#2034`, `#1563`, `#1575`) are classified as inputs, child work, or downstream consumers rather than duplicated scope
- [ ] New child issues (`#2206`–`#2209`) are linked with explicit dependency order and rationale
- [ ] Parent doc justifies its canonical location and discoverability from existing intelligence docs/issues
- [ ] Plan review artifacts are saved under `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | required explicit canonical identity rule, owner map, allowed/forbidden flows, child guardrails, and architectural-only handling of unified artifact registry |
| Codex | MINOR | parent plan should make approval-gate summary and issue classification explicit, but current scope separation is directionally correct |
| Gemini | MINOR | recommended future machine-readable conformance checks and warned against parent-scope schema/enforcement creep |

Overall result: REVISED (one MAJOR addressed in current draft; final re-review still required before plan-review)

Revisions made based on review:
- redefined `#2206` as conformance validation rather than pyramid-definition work
- moved parent operating-model doc into an existing docs surface under `docs/document-intelligence/`
- locked in parent-level canonical `doc_key` identity rule and degraded/offline fallback policy
- added explicit owner map, allowed/forbidden flows, named exceptions, and issue classification/guardrails
- resolved unified artifact registry question at parent level as an architectural requirement only, with schema delegated to `#2207`/`#2136`

---

## Risks and Open Questions

- Risk: if `#2205` directly edits registry schemas or retrieval-enforcement mechanics, it will duplicate `#2136`, `#2207`, and `#2208`.
- Risk: if the operating-model doc is too abstract, children may still diverge; dependency order and ownership boundaries must be explicit.
- Open: should the parent doc introduce a named unified artifact-registry concept now, or leave that exact artifact shape to `#2207`/`#2136` while still specifying only the architectural requirement?
- Open: should weekly-review consumption (`#2089`) remain a downstream consumer only, or should `#2205` also minimally update weekly-review docs to reference the pyramid once approved?
- Dependency order (explicit): (1) `#2205` parent operating model, (2) `#2207` provenance + reuse contract, (3) `#2209` durable/transient boundary policy, (4) `#2096` accessibility map, (5) `#2104` canonical entry points, (6) `#2136` accessibility registry, (7) `#2208` workflow retrieval contract, (8) `#2206` conformance checks, (9) `#2089` weekly review consumption/verification.

---

## Complexity: T3

T3 — this is an architectural parent issue spanning multi-machine knowledge systems, provenance, workflow policy, and issue-tree decomposition across several existing issues and multiple follow-on contracts.
