# LLM-Wiki + Resource/Document Intelligence Operating Model

> **Issue:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205)
> **Status:** Normative — approved parent architecture for the intelligence ecosystem
> **Date:** 2026-04-11
> **Scope:** Architecture and contracts only. Implementation delegated to child issues.

---

## 1. Purpose and Scope

### What this document defines

This is the **parent operating model** for the workspace-hub intelligence ecosystem. It establishes:

- A single-source-of-truth pyramid with explicit layer ownership
- Canonical document identity rules
- Allowed and forbidden information flows between layers
- Cross-machine access semantics
- Scope boundaries for child issues

### What this document does NOT define

This document is architecture-only. The following are explicitly **delegated to child issues**:

| Delegated concern | Owner issue |
|---|---|
| Registry schemas and provenance implementation | #2207, #2136 |
| Conformance validation scripts | #2206 |
| Retrieval contract for issue workflows | #2208 |
| Durable-vs-transient boundary details | #2209 |
| Weekly review consumption patterns | #2089 |
| LLM-wiki ingestion pipeline implementation | #2034 |

No code, YAML schemas, enforcement hooks, or CLI tools are defined here.

---

## 2. Single-Source-of-Truth Pyramid

The intelligence ecosystem is organized into six layers. Each layer has exactly one owner concern. Layers consume from the layer below and produce for the layer above.

### Layer definitions and owner map

| Layer | # | Owns | Must NOT own | Primary artifact examples |
|---|---|---|---|---|
| **Source documents** | L1 | Raw external/source files and their original locations | Promoted summaries, workflow state, narrative synthesis | Mounted sources at `/mnt/ace`, external PDFs, conference papers, standards documents |
| **Registry / provenance** | L2 | Inventory, content hashes, file paths, extraction lineage, availability status | Durable narrative knowledge, issue state | `data/document-index/registry.yaml`, `data/document-index/standards-transfer-ledger.yaml`, `data/document-index/mounted-source-registry.yaml`, manifests, ledgers |
| **Durable knowledge** | L3 | Distilled reusable knowledge and conceptual synthesis | Live execution state, source-of-truth provenance records | `knowledge/wikis/**`, LLM-wiki pages, promoted summaries |
| **Entry-point** | L4 | Human/agent navigation surfaces into the intelligence system | Raw source inventory, execution state | Accessibility maps (#2096), canonical entry points (#2104), index pages |
| **Execution state** | L5 | Scope, ownership, approval state, acceptance criteria, delivery tracking | Durable technical knowledge, provenance truth | GitHub issues, plans under `docs/plans/`, review artifacts |
| **Transient session** | L6 | Handoffs, research notes, working context, temporary synthesis candidates | Canonical durable knowledge, canonical execution state | `.planning/`, handoff docs, session artifacts, agent scratchpads |

### Ownership invariant

Every artifact in the intelligence ecosystem belongs to exactly one layer. If an artifact appears to serve two layers, it must be split or assigned to the layer that owns its primary concern. Ambiguous cases are resolved by the **most-durable-owner rule**: assign to the lowest-numbered layer whose ownership definition covers the artifact's primary purpose.

---

## 3. Canonical Document Identity

### The doc_key rule

The canonical identity of any source document is **content-based**: a `doc_key` derived from the document's content hash (SHA-256 or equivalent).

- **File paths are aliases.** The same document may appear at multiple paths across machines, mounts, and cache locations. These paths are metadata about the document, not its identity.
- **Path never outranks content identity.** When two paths resolve to the same `doc_key`, they are the same document regardless of location.
- **Registries must refer to `doc_key`.** All registry entries, manifests, summaries, promoted artifacts, and wiki-ready records must reference the canonical `doc_key` rather than inventing separate identities from paths alone.
- **Path is retained for provenance and reachability.** Every known path for a document is recorded as an alias with availability metadata (machine, mount, last-verified timestamp).

### Identity across machines

When the same document exists on multiple machines:
- The `doc_key` is authoritative. Path differences do not create separate documents.
- If a document is modified on one machine, it becomes a new `doc_key`. The old and new keys may be linked via provenance lineage but are distinct documents.

---

## 4. Allowed Information Flows

Information flows **upward** through the pyramid (lower layers feed higher layers) and **downward** for consumption (higher layers read from lower layers). Each flow is directional.

### Permitted flows

| From | To | Flow description |
|---|---|---|
| L1 Source documents | L2 Registry/provenance | Indexing, hashing, extraction status tracking |
| L2 Registry/provenance | L3 Durable knowledge | Promotion of structured outputs into wiki pages; cross-linking to registry entries |
| L2 Registry/provenance | L4 Entry-point surfaces | Feeding accessibility maps, navigation indexes |
| L3 Durable knowledge + L2 Registry | L5 Execution state | Issue planning, execution, and review consume existing intelligence as evidence |
| L6 Transient session | L3 Durable knowledge | Promotion of session findings into wiki pages — **only after explicit promotion decision** |
| L5 Execution state | L3 Durable knowledge | Post-issue promotion of validated findings — issues are **never** the durable store themselves. Note: this is not circular with L3→L5 above; L5 *reads* L3 as evidence (consumption), while this flow is a one-time *write-back* of validated results (promotion). Neither layer claims the other as its source of truth. |

### Multi-machine flow rule

All flows must work identically regardless of which machine originates or consumes the data, subject to the cross-machine access model (Section 7). The `doc_key` is the join key across machines.

---

## 5. Forbidden Information Flows

These patterns are anti-patterns. Agents and pipelines must not create them.

| Anti-pattern | Why it is forbidden |
|---|---|
| **LLM-wikis reparsing raw documents** when sufficient registry/promoted evidence already exists at L2 | Creates duplicate extraction work; risks inconsistency between wiki content and registry provenance |
| **GitHub issues acting as the durable knowledge base** | Execution state (L5) must not become the source of truth for technical knowledge; issues close and become stale |
| **Transient session artifacts becoming canonical** without explicit promotion to L3 | Session handoffs, research notes, and scratchpads decay; they must be promoted or discarded |
| **Entry-point docs inventing new provenance facts** not backed by L2 registry/provenance layer | Entry points (L4) navigate to truth; they must not create it |
| **Path-only identity creating duplicate truth** for the same content across machines | Violates the `doc_key` rule; creates competing sources of truth for the same document |
| **Circular flows** between any two layers where each claims the other as source | Breaks the directional flow invariant; creates infinite update loops |

---

## 6. Named Exceptions

Two categories of cross-layer access are explicitly permitted despite the directional flow rules:

### Audit and provenance lookbacks

Audit processes (including conformance checks under #2206 and weekly reviews under #2089) may **read across any layers** to verify lineage, consistency, and completeness. Audit reads do not create new source-of-truth claims; they verify existing ones.

### Degraded / offline mode

When a shared mount or artifact store is unreachable:

- Git-tracked metadata at L2 (registry entries, ledger rows) remains the **minimal cross-machine truth**.
- Cached copies of L2/L3 artifacts may serve read-through requests, but must:
  - Preserve the canonical `doc_key` reference
  - Mark availability state as `degraded` or `unavailable`
  - Never silently become canonical without explicit re-promotion when connectivity is restored
- Local caches are **performance layers only** — they accelerate reads but do not establish provenance or ownership.

---

## 7. Cross-Machine Access Model

The intelligence ecosystem spans multiple machines (workstations, servers, mounted drives). Access is governed by a three-tier model:

| Tier | What it provides | Availability | Examples |
|---|---|---|---|
| **Git-tracked metadata** | Registry entries, ledger rows, wiki pages, issue references | Always available (repo clone) | `data/document-index/*.yaml`, `knowledge/wikis/**`, `docs/plans/` |
| **Shared derived artifacts** | Summaries, extractions, promoted outputs, batch results | Available when shared mounts are reachable | `/mnt/ace/` outputs, overnight batch results |
| **Local caches** | Read-through copies of L1/L2/L3 artifacts for performance | Machine-local only | Local extraction caches, downloaded PDFs |

### Access rules

1. **Git-tracked metadata is always authoritative** for L2 registry state and L3 wiki content.
2. **Shared derived artifacts are preferred** for large outputs (summaries, extractions) when reachable.
3. **Local caches must not silently become canonical.** If a local cache diverges from git-tracked or shared state, the cache is stale — not the other way around.
4. **Machine reachability is explicit metadata**, not an assumption. Each registry entry should record which machines/mounts can access the underlying source document (implementation details delegated to #2136).

---

## 8. Unified Artifact Registry — Architectural Requirement

### The concept

The intelligence ecosystem requires a **single lookup model** that can map any `doc_key` to:
- Source references (paths, mounts, URLs)
- Registry/provenance entries (extraction status, lineage)
- Promoted artifacts (summaries, wiki entries)
- Execution references (related issues, plans)

This is an architectural requirement: one conceptual registry that unifies currently separate tracking surfaces.

### What is NOT defined here

- The concrete schema for this registry
- The file format or storage location
- The implementation approach (single file vs. federated lookups)
- The query interface

These details are delegated to #2207 (provenance contract) and #2136 (accessibility registry). This document requires only that child implementations converge on a single `doc_key`-based lookup model rather than inventing incompatible identity systems.

---

## 9. Issue Tree and Dependency Order

### Issue classification

| Issue | Title | Classification | Role relative to #2205 |
|---|---|---|---|
| #2034 | engineering LLM wiki seed + incremental ingest pipeline | Input / upstream producer | Provides existing llm-wiki ingest capability |
| #1563 | consolidated data/resource intelligence feature | Input / upstream program | Provides broader data/resource-intelligence umbrella |
| #1575 | holistic document/resource intelligence architecture | Input / upstream architecture | Provides multi-source resource-intelligence framing |
| #2207 | standards/codes provenance + reuse contract | Child contract | Defines provenance schema and reuse rules under this model |
| #2209 | durable-vs-transient knowledge boundary policy | Child policy | Defines detailed boundary rules under this model |
| #2096 | intelligence accessibility map | Child implementation | Builds accessibility inventory/map |
| #2104 | canonical entry points for ecosystem intelligence | Child implementation | Designs L4 entry-point surfaces |
| #2136 | intelligence accessibility registry with machine reachability | Child implementation | Builds machine-readable L2/L4 registry |
| #2208 | intelligence retrieval contract for issue workflows | Child workflow contract | Defines how L5 execution state consumes L2/L3 |
| #2206 | conformance checks against approved pyramid | Child validation | Validates that implementations conform to this model |
| #2089 | weekly ecosystem execution/intelligence review | Downstream consumer | Verifies freshness and accessibility against this model |

### Dependency order

Implementation should proceed in this order. Each issue may begin only when its predecessors have established the contracts it depends on.

```
1. #2205  Parent operating model (this document)
2. #2207  Provenance + reuse contract
3. #2209  Durable/transient boundary policy
4. #2096  Accessibility map
5. #2104  Canonical entry points
6. #2136  Accessibility registry
7. #2208  Workflow retrieval contract
8. #2206  Conformance checks
9. #2089  Weekly review consumption/verification
```

---

## 10. Scope Boundaries — Child Issue Guardrails

Each child issue operates within the architectural framework defined here. The following table specifies what each child **may implement** and what it **must not redefine**.

| Child issue | May implement | Must NOT redefine |
|---|---|---|
| #2206 | Conformance validation scripts, linters, automated checks against this model | The pyramid layers, ownership model, or flow rules |
| #2207 | Provenance schema, reuse contract, `doc_key` implementation details, promotion rules | Parent ownership model, layer boundaries, or workflow policy |
| #2208 | Retrieval hooks for issue planning/execution/review, evidence requirements | Provenance schema, pyramid ownership, or `doc_key` definition |
| #2209 | Detailed boundary criteria for durable vs transient artifacts, promotion/expiration rules | Provenance schema, accessibility registry design, or `doc_key` definition |
| #2096 | Accessibility inventory, map visualization, coverage analysis | Canonical layer ownership, document identity, or workflow policy |
| #2104 | Entry-point page design, navigation structure, index format | Provenance ownership, execution-state policy, or `doc_key` rules |
| #2136 | Machine-readable registry implementation, reachability metadata schema | Parent pyramid contract, durable/transient boundary, or `doc_key` definition |

### Conflict resolution

If a child issue discovers that this operating model is insufficient or incorrect for its implementation needs, the child must:
1. Document the conflict in a comment on this parent issue (#2205)
2. Propose a specific amendment
3. Wait for user approval before deviating from the model

Child issues must NOT silently redefine parent-level contracts.

---

## 11. Discoverability

### Why this location

This document lives at `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` because:
- `docs/document-intelligence/` is the existing home for intelligence-ecosystem architecture documents
- Sibling documents include `holistic-resource-intelligence.md`, `data-intelligence-map.md`, and `engineering-documentation-map.md`
- This location is already indexed by agent context and discovery tools

### Cross-links

The following documents and issues should reference this operating model:

| Artifact | How it should reference this document |
|---|---|
| `docs/document-intelligence/holistic-resource-intelligence.md` | As the parent architectural authority for resource intelligence |
| `docs/assessments/document-intelligence-audit.md` | As the governing model for pipeline layer classification |
| `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | As the pyramid definition used for freshness/accessibility audits |
| `knowledge/wikis/engineering/wiki/index.md` | As the authority for L3 durable-knowledge layer scope |
| GitHub issues #2206, #2207, #2208, #2209 | As the parent contract they implement under |
| `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Child contract for #2207 — defines provenance fields and reuse rules under this model |
| `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Child policy for #2209 — defines durable/transient classification and promotion rules |
| `docs/document-intelligence/intelligence-accessibility-map.md` | Child implementation for #2096 — inventories intelligence assets and identifies discoverability gaps |
| `docs/document-intelligence/pyramid-conformance-checks.md` | Child validation design for #2206 — defines conformance checks against this model |
| `docs/plans/README.md` | Via the #2205 plan index row |

### Agent discovery

Agents consulting the intelligence ecosystem should be directed here as the canonical starting point for understanding layer ownership, information flow, and scope boundaries.

---

## 12. Open Questions — True Residuals

These questions remain genuinely open and should be resolved during child-issue implementation:

1. **Unified registry convergence**: Will #2207 and #2136 converge on a single registry file or a federated lookup across existing files? This model requires convergence on `doc_key` but does not prescribe the mechanism.

2. **Weekly review scope expansion**: Should #2089 (weekly review) be updated to explicitly reference this pyramid once approved, or does it remain a downstream consumer only? Recommend keeping it downstream unless review coverage gaps are discovered.

3. **Programmatic enforcement timeline**: Gemini's adversarial review noted that a static markdown document may be insufficient to govern multi-agent workflows long-term. #2206 (conformance checks) addresses this, but the timeline for automated enforcement is not fixed.

4. **Cross-machine path normalization**: When a document's path changes across machines (e.g., `/mnt/ace/standards/` vs. `/d/standards/`), do we need an explicit alias-resolution service or is registry-level path recording sufficient? Likely sufficient for now, but worth revisiting under #2136.
