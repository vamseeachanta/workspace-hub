# Prioritization Spine — Resource/Document Intelligence Backlog

> **Issue:** [#2248](https://github.com/vamseeachanta/workspace-hub/issues/2248)
> **Children:** [#2249](https://github.com/vamseeachanta/workspace-hub/issues/2249) (other-bucket triage), [#2250](https://github.com/vamseeachanta/workspace-hub/issues/2250) (stale artifact reconciliation)
> **Date:** 2026-04-14
> **Status:** Active — execution order for the document intelligence backlog

---

## Purpose

This document establishes the explicit execution order for the resource/document intelligence backlog. It cross-links existing issues into a sequenced plan grounded in current coverage data, so future runs improve usable file-context fastest.

## Current Coverage Snapshot

| Metric | Value | Source |
|---|---|---|
| Total index records | 1,033,933 | `data/document-index/resource-intelligence-maturity.yaml` |
| Records with summaries | 639,585 (61.9%) | `data/document-index/resource-intelligence-maturity.yaml` |
| Unsummarized gap | ~394,348 | Derived |
| Index-level `other` records | 44,705 | `data/document-index/data-audit-report.md` |
| Standards-level `other` | 0 (eliminated) | `data/document-index/resource-intelligence-maturity.yaml` |
| Online resources not started | 221 | `data/document-index/online-resource-registry.yaml` |
| Standards documents in scope | 425 | `data/document-index/resource-intelligence-maturity.yaml` |
| Standards documents read | 29 (6.8%) | `data/document-index/resource-intelligence-maturity.yaml` |

## Execution Order

### P0 — Semantic Context Coverage

> **Rationale:** The largest single gap. 394K unsummarized records degrade every downstream consumer — issue planning, retrieval, wiki promotion. Must run first.

| Order | Issue | Title | State | Dependency |
|---|---|---|---|---|
| 0.1 | [#1924](https://github.com/vamseeachanta/workspace-hub/issues/1924) | Execute Phase B summarization — batch to 90% | OPEN | None — standalone batch |
| 0.2 | [#2249](https://github.com/vamseeachanta/workspace-hub/issues/2249) | Triage index-level `other` bucket into bounded packs | OPEN | Benefits from #1924 progress but can start in parallel |

**Exit criteria:** Summary coverage exceeds 85%; `other` bucket segmented into actionable packs.

### P1 — Retrieval/Discoverability Contract

> **Rationale:** The operating model, accessibility map, and registry coherence define *how agents find things*. This must be in place before expanding sources or running automation that depends on registry correctness.

| Order | Issue | Title | State | Dependency |
|---|---|---|---|---|
| 1.1 | [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) | Multi-machine llm-wiki + resource/doc intelligence operating model | OPEN | None — framework issue |
| 1.2 | [#2096](https://github.com/vamseeachanta/workspace-hub/issues/2096) | Intelligence accessibility map | OPEN | Informed by #2205 model |
| 1.3 | [#2105](https://github.com/vamseeachanta/workspace-hub/issues/2105) | Freshness cadences and staleness signals | OPEN | Needs #2205 layer model |
| 1.4 | [#2149](https://github.com/vamseeachanta/workspace-hub/issues/2149) | Seeded intelligence accessibility registry generation | OPEN | Needs #2096 map |
| 1.5 | [#2156](https://github.com/vamseeachanta/workspace-hub/issues/2156) | Registry coherence validator | OPEN | Needs #2149 registry |
| 1.6 | [#2168](https://github.com/vamseeachanta/workspace-hub/issues/2168) | Cross-registry coverage/drift report | OPEN | Needs #2156 validator |

**Exit criteria:** Accessibility registry is coherent, validated, and drift-checked.

### P2 — Source Expansion with Token Discipline

> **Rationale:** Download and ingest new sources only after the retrieval contract exists to guide selection and the prioritization queue ranks candidates by token efficiency.

| Order | Issue | Title | State | Dependency |
|---|---|---|---|---|
| 2.1 | [#2242](https://github.com/vamseeachanta/workspace-hub/issues/2242) | Prioritize external-source queue for token-efficient wiki strengthening | CLOSED | Complete |
| 2.2 | [#1609](https://github.com/vamseeachanta/workspace-hub/issues/1609) | Automated resource download pipeline | OPEN | Uses queue from #2242; needs P1 registry correctness |
| 2.3 | [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) | Audit /mnt/ace for undiscovered resources | OPEN | Independent scan, but results feed into P1 registries |

**Exit criteria:** Download pipeline operational; undiscovered-resource audit complete.

### P3 — Umbrella/Ledger Hygiene

> **Rationale:** Control-plane cleanup. Stale summaries cause agents to prioritize the wrong work. Should run after or alongside P1 to benefit from the coherence infrastructure.

| Order | Issue | Title | State | Dependency |
|---|---|---|---|---|
| 3.1 | [#2250](https://github.com/vamseeachanta/workspace-hub/issues/2250) | Reconcile stale intelligence summary artifacts against canonical ledgers | OPEN | Can start now; benefits from #2156 validator |
| 3.2 | [#1563](https://github.com/vamseeachanta/workspace-hub/issues/1563) | Data & resource intelligence consolidated plan | OPEN | Umbrella — updated as children close |

**Exit criteria:** No known drift between summary artifacts and canonical YAML ledgers; source-of-truth ownership explicit.

## Dependency Map

```
P0 (semantic coverage)
  #1924 batch summarization ──────────────────────────────┐
  #2249 other-bucket triage ──────────────────────────────┤
                                                          │
P1 (retrieval contract)                                   │
  #2205 operating model ─┐                                │
  #2096 accessibility map ┤                               │
  #2105 freshness signals ┘                               │
       └─► #2149 seeded registry                          │
              └─► #2156 coherence validator                │
                     └─► #2168 drift report ──────────────┤
                                                          │
P2 (source expansion)                      needs P1 ◄─────┤
  #2242 priority queue [DONE] ─► #1609 download pipeline  │
  #1579 undiscovered-resource audit ──────────────────────┤
                                                          │
P3 (ledger hygiene)                                       │
  #2250 stale artifact reconciliation ────────────────────┘
  #1563 umbrella (updated as children close)
```

## Key Sequencing Rules

1. **Summary coverage and `other`-bucket triage (P0) precede** broad wiki promotion for ambiguous source families
2. **Accessibility/freshness/coherence work (P1) precedes** automation that depends on registry correctness (P2)
3. **External-source download/ingest (P2) uses** the retrieval contract and prioritization queue, not raw expansion
4. **Stale artifact reconciliation (P3)** can start early but reaches full value after the coherence validator (#2156) exists

## Parallelism Opportunities

- **P0.1 + P0.2**: Summarization and other-bucket triage can run concurrently
- **P0 + P1.1-1.3**: Coverage work and operating model/framework issues are independent
- **P3.1 early start**: Stale artifact reconciliation can begin immediately alongside P0/P1
- **P2.1 already complete**: #2242 is closed, removing a blocker for #1609
