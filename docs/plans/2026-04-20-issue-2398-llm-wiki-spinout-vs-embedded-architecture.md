# Plan for #2398: Assess llm-wiki spinout vs embedded workspace-hub architecture

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2398
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2398-claude.md | scripts/review/results/2026-04-20-plan-2398-codex.md | scripts/review/results/2026-04-20-plan-2398-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — parent architecture for the intelligence ecosystem; explicitly delegates llm-wiki ingestion and child concerns rather than repo-boundary decisions.
- Found: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — classifies llm-wikis as L3 durable knowledge and distinguishes them from L5/L6 execution/transient artifacts.
- Gap: no explicit architecture decision document compares embedded-vs-spinout repo boundaries for llm-wikis.

### Standards
| Standard | Status | Source |
|---|---|---|
| Intelligence ecosystem parent operating model | done | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` |
| Durable-vs-transient policy | done | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` |
| Control-plane contract for repo adapters | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — proves existing wiki index/navigation surface that a spinout or split would have to preserve.
- `knowledge/wikis/engineering/wiki/entities/llm-wiki-tool.md` — concrete llm-wiki entity page proving current embedded durable-knowledge location.
- `knowledge/wikis/engineering/CLAUDE.md` — shows per-wiki configuration/authority surface that would need an ownership decision in any spinout/hybrid path.

### Documents consulted
- Related issue #2390 — current llm-wiki strengthening roadmap; proves the embedded system now has enough scope to justify a boundary review.
- Related issue #2034 — engineering LLM wiki seed + incremental ingest pipeline; critical current-state coupling surface for ingestion ownership.
- Related issue #2366 — llm-wiki strengthening scorecard and prioritized action queue; relevant navigation and governance coupling surface.
- Related issue #2205 — parent operating model for the intelligence ecosystem.
- Related issues #2206, #2207, #2209 — conformance, provenance, and durable/transient sibling contracts shaping what would have to move if a spinout occurs.
- `docs/reports/2026-04-20-refactor-knowledge-release-readiness-dependency-map.md` — marks #2398 as a strategy lane that should not block current strengthening-wave execution by default.
- Existing issue body for #2398 — explicitly requires follow-up implementation issues when the recommendation is spinout or partial split.

### Gaps identified
- No current-state dependency map of llm-wiki coupling to workspace-hub scripts, docs, registries, and review workflows.
- No option matrix comparing stay-embedded vs single-repo spinout vs split-core/content architecture.
- No migration-risk or rollback framework for link rot, CI ownership, and search/index responsibilities.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md |
| Coupling inventory | docs/reports/2026-04-20-issue-2398-llm-wiki-coupling-inventory.md |
| Decision report + migration outline | docs/reports/2026-04-20-issue-2398-llm-wiki-boundary-options.md |
| Conditional follow-up issue drafts | docs/reports/2026-04-20-issue-2398-follow-up-issue-drafts.md |
| Plan review — Claude | scripts/review/results/2026-04-20-plan-2398-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-20-plan-2398-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-20-plan-2398-gemini.md |
| Docs updates | docs/plans/README.md |

---

## Deliverable

A documented architecture recommendation for whether llm-wikis should remain embedded in workspace-hub, spin out into a dedicated repo, or adopt a hybrid core/content split, plus conditional follow-up issue drafts if movement is recommended.

---

## Pseudocode

```
build a concrete coupling inventory across docs, registries, scripts, issue workflows, navigation surfaces, provider adapters, #2034 ingestion ownership, and both static + known runtime/CI coupling surfaces
capture current strengths and bottlenecks of the embedded architecture from that evidence
use explicit decision weighting: coupling impact, operational isolation, cross-repo reuse, migration cost, rollback difficulty
define three options: stay_embedded, standalone_repo, split_core_plus_content
for each option:
    score coupling, portability, CI boundaries, search/index ownership, contribution ergonomics, migration risk, and rollback difficulty
    assign explicit ownership for ingestion, search/index build, backlinks, versioning, and CI
identify which concerns are solved immediately and which are merely relocated
recommend one option with explicit decision criteria, non-goals, and do-not-freeze notes for current #2390 execution waves
if recommendation implies movement:
    include a distinct migration-plan-outline section in the decision report with headers for repo boundaries, sync/backlink strategy, release/versioning model, search/index ownership, path/link migration plan, and rollback path
    generate conditional follow-up implementation issue drafts only after the migration-plan-outline exists
write coupling inventory, decision report with embedded migration outline, and conditional issue-draft pack
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/2026-04-20-issue-2398-llm-wiki-coupling-inventory.md | concrete path-level dependency inventory including static and known runtime/CI coupling |
| Create | docs/reports/2026-04-20-issue-2398-llm-wiki-boundary-options.md | option matrix, recommendation, and migration-plan outline in one cohesive artifact |
| Create | docs/reports/2026-04-20-issue-2398-follow-up-issue-drafts.md | conditional implementation issue drafts if movement is recommended |
| Update | docs/plans/README.md | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_coupling_inventory_covers_required_surfaces | embedded-state analysis is concrete | current docs/issues/paths | inventory spans scripts/docs/registries/workflows/adapters including #2034 ingestion and known runtime/CI coupling |
| test_coupling_inventory_captures_hardcoded_llm_wiki_references | inventory is evidence-backed | grep/AST scan over repo references | hardcoded `llm-wiki` references accounted for |
| test_options_matrix_has_three_distinct_architectures | decision space is real, not binary hand-waving | option definitions | 3 compared options |
| test_recommendation_has_ecosystem_rationale | choice is justified beyond convenience | final report | decision criteria + recommendation |
| test_migration_outline_contains_required_headers | required migration structure exists when movement is recommended | decision report | headers for repo boundaries, sync/backlink strategy, release/versioning model, search/index ownership, path/link migration plan, rollback path |
| test_follow_up_issue_drafts_are_conditional | movement work is actionable but not assumed | final recommendation | issue drafts only when spinout/hybrid is chosen |
| test_option_ownership_is_explicit | search/index/backlink/CI/versioning ownership is assigned | option matrix | explicit owners per option |

---

## Acceptance Criteria

- [ ] A coupling inventory exists at `docs/reports/2026-04-20-issue-2398-llm-wiki-coupling-inventory.md`
- [ ] A decision report + migration outline exists at `docs/reports/2026-04-20-issue-2398-llm-wiki-boundary-options.md`
- [ ] The coupling inventory maps current llm-wiki coupling to workspace-hub concretely, including #2034 ingestion and #2366 scorecard surfaces
- [ ] The coupling inventory includes static plus known runtime/CI coupling surfaces relevant to repo-boundary risk
- [ ] The decision report compares at least three architecture options with trade-offs
- [ ] The decision report assigns explicit ownership for ingestion, search/index build, backlinks, CI, and versioning per option
- [ ] If spinout/hybrid is recommended, the decision report contains an explicit migration-plan outline with rollback path and required subsection headers
- [ ] The decision report recommends one option with explicit reasoning and non-goals
- [ ] If spinout/hybrid is recommended, a conditional issue-draft pack exists at `docs/reports/2026-04-20-issue-2398-follow-up-issue-drafts.md`
- [ ] If stay-embedded is recommended, the decision report explicitly records why no follow-up migration issues were created
- [ ] Review artifacts are posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Awaiting review |
| Codex | PENDING | Awaiting review |
| Gemini | PENDING | Awaiting review |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** the strategy review could accidentally freeze or derail currently useful llm-wiki execution work if it is framed as a prerequisite rather than a boundary decision.
- **Risk:** a spinout recommendation could underestimate backlink, search-index, or sync complexity across existing docs and scripts.
- **Open:** should the recommendation optimize for authoring convenience, operational isolation, or cross-repo reuse first when trade-offs conflict?

---

## Complexity: T2

**T2** — bounded architecture/strategy plan requiring multi-source analysis and explicit option comparison, but not immediate code migration.
