# Refactor / Knowledge / Release-Readiness Dependency Map

Date: 2026-04-20
Context issues: #1962, #2390, #2397, #2398, #2399

## Purpose
Provide a dependency-aware execution and approval sequence for the new refactor-adjacent planning issues without letting the umbrella issues absorb unrelated scope by drift.

## Current issue roles

| Issue | Role | Type | Notes |
|---|---|---|---|
| #1962 | Tier-1 ecosystem refactor umbrella | steering umbrella | Broad parent for repo refactoring; should consume outputs from narrower child tracks rather than directly absorbing them |
| #2390 | llm-wiki strengthening roadmap | execution-roadmap umbrella | Sequences current llm-wiki strengthening waves; should not decide repo-boundary strategy by drift |
| #2397 | canonical folder-structure and repo anatomy contract | structural design child | Defines repo layout normalization and migration rules |
| #2398 | llm-wiki spinout assessment | strategy child | Decides whether llm-wiki stays embedded, spins out, or becomes hybrid |
| #2399 | next-model-release readiness contract | control-plane readiness child | Future-proofs adapters, prompts, logs, and evaluation surfaces for provider/model evolution |
| #1567 | continuous repo architecture intelligence | evidence feeder | Supplies cross-repo architecture discovery and staleness detection context |
| #1603 | multi-repo architecture scan | evidence feeder | Supplies repo-level architecture summaries for tier-1 repos |
| #1661 | dependency cycle / layering detection | evidence feeder | Supplies structural risk signals that can inform #2397 and #1962 |

## Hard dependencies

1. #2397 depends on existing taxonomy and control-plane standards, not on implementation under #1962.
   - Inputs: `docs/standards/FILE_STRUCTURE_TAXONOMY.md`, `docs/standards/CONTROL_PLANE_CONTRACT.md`, #1567, #1603, #1661

2. #2398 depends on the current llm-wiki operating model and current strengthening roadmap.
   - Inputs: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, #2390, #2205, #2206, #2207, #2209
   - Important: #2398 should NOT block current strengthening-wave work under #2390 unless the assessment explicitly recommends a freeze.

3. #2399 depends on the current control-plane and review-routing contracts.
   - Inputs: `docs/standards/CONTROL_PLANE_CONTRACT.md`, `docs/standards/AI_REVIEW_ROUTING_POLICY.md`, #2089, #1583, #2323

4. #1962 should consume the outputs of #2397 and #2399 before major execution planning, because structural refactors and model-readiness constraints materially shape the implementation surface.

5. #1962 may optionally consume #2398 if llm-wiki boundaries affect repo-organization decisions, but #2398 is not a strict blocker for non-wiki tier-1 refactor work.

## Soft dependencies / sequencing preferences

| From | To | Why |
|---|---|---|
| #2397 | #1962 | Repo anatomy contract reduces refactor churn and clarifies migration boundaries |
| #2399 | #1962 | Future model/provider constraints should shape refactor-friendly control-plane decisions |
| #2390 | #2398 | Spinout assessment needs the current roadmap and coupling picture |
| #2398 | #1962 | If llm-wiki spinout is recommended, umbrella refactor planning should account for repo-boundary changes |
| #1567/#1603/#1661 | #2397 and #1962 | Architecture evidence improves repo-structure decisions and prioritization |

## Recommended approval / execution order

### Wave A — approve the focused child planning lanes first
1. #2397 — repo anatomy / folder-structure contract
2. #2398 — llm-wiki spinout assessment
3. #2399 — next-model-release readiness contract

These are narrower, decision-oriented issues and create reusable constraints for broader umbrellas.

### Wave B — refresh umbrella steering using child outputs
4. #1962 — re-baseline umbrella sequencing using #2397 and #2399 outputs, plus #2398 if it changes repo boundaries
5. #2390 — keep as execution roadmap for the embedded llm-wiki workstream, with a link to #2398 as the separate strategy lane

## Parallelization guidance

Safe to plan/review in parallel:
- #2397 and #2399
- #2398 can also run in parallel, provided it is treated as strategy-only and does not rewrite #2390 scope mid-review

Not safe to execute as one merged issue:
- #2397 + #2398 + #2399 + #1962 together

Reason: these issues answer different questions (structure, boundary, future-readiness, umbrella steering). Merging them would blur acceptance criteria and block approval on unrelated concerns.

## Approval recommendation

For immediate user review/approval, prioritize:
1. #2397
2. #2398
3. #2399

Then use approved results to amend #1962 and, if needed, annotate #2390.
