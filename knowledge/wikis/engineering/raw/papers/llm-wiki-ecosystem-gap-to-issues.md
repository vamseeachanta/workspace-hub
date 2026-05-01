# Archived Skill: `llm-wiki-ecosystem-gap-to-issues`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues`
Consolidation date: 2026-04-29

---

---
name: llm-wiki-ecosystem-gap-to-issues
description: Review the workspace-hub LLM-wiki/document-intelligence ecosystem, identify high-leverage gaps, and create grounded GitHub feature issues without duplicating existing work.
version: 1.0.0
category: workspace-hub-learned
type: workflow
trigger: manual
auto_execute: false
tags:
  - llm-wiki
  - github-issues
  - knowledge-management
  - workspace-hub
  - gap-analysis
---

# LLM-wiki ecosystem gap -> GitHub issues

Use when the user asks to review the repo/document ecosystem and create new issues to strengthen LLM-wikis.

## Goal

Turn ecosystem review into a small set of non-duplicate, high-leverage GitHub issues grounded in live repo state rather than intuition.

## Required evidence sources

Read these before proposing issues:

1. Live GitHub issue search
   - `gh issue list --search 'llm-wiki OR knowledge wiki OR wiki ingest OR knowledge/wikis'`
   - Then narrower searches for the exact candidate theme to avoid duplicates.
2. Architecture / review docs
   - `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
   - `docs/reports/2026-04-16-llm-wiki-resource-intelligence-unified-review.md`
3. Priority/execution artifacts
   - `docs/reports/llm-wiki-external-source-priority-queue.md`
   - `docs/reports/llm-wiki-staged-batch-packs.md`
4. Discoverability / provenance gaps
   - `docs/document-intelligence/intelligence-accessibility-map.md`
   - `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
5. Live repo facts
   - Count wiki pages directly from `knowledge/wikis/*/wiki/**/*.md`
   - Check cross-link artifacts (`knowledge/wikis/cross-links.md`, `cross-links.jsonl` if present)
   - Inspect `data/design-codes/code-registry.yaml` when proposing standards/registry-driven strengthening

## Proven issue themes that are worth checking first

These themes produced grounded issue opportunities:

1. `wiki_refs` reverse lookup
   - Trigger: architecture/provenance docs define the contract, but live repo still lacks registry -> wiki reverse lookup.
   - Signal: accessibility map says affected wiki pages can only be found with grep.
2. External-source promotion packs
   - Trigger: priority queue + staged batch pack already exist, but execution issue is missing.
   - Signal: thin wiki domains (engineering / naval-architecture / maritime-law) plus metadata-rich source families ready for promotion.
3. Design-code registry promotion into wiki surfaces
   - Trigger: `data/design-codes/code-registry.yaml` has rich edition/repo metadata but is not linked from standards wiki surfaces.
4. Wiki strengthening scorecard
   - Trigger: health/lint exists, but prioritization across domains/source families is still ad hoc.
5. Large-domain navigation repair
   - Trigger: a wiki domain is technically discoverable but functionally unusable because `wiki/index.md` is huge or uncurated.
   - Signal: live line counts show monolithic indexes (for example 20k+ lines) and the accessibility map says there is no curated entry beyond the index.
6. Source-title aliasing
   - Trigger: source pages exist, but titles are mostly raw filenames or numeric IDs.
   - Signal: live sampling/counts show most source-page frontmatter titles look like `spe143317.pdf` or `22035.pdf` instead of human-readable titles.
7. Closed-issue / transient-to-durable promotion substrates
   - Trigger: the repo has policy for L5/L6 -> L3 promotion, but not the operational ledger/queue to execute it.
   - Signal: broad closed-issue backlog, handoff/review corpora, or WRK completion archives exist without structured promotion routing.
8. Provenance backfill on legacy wiki pages
   - Trigger: newer provenance rules (`doc_key`, `promoted_from`, `wiki_refs`) are ahead of older wiki content.
   - Signal: existing pages/logs lack deterministic promotion lineage even though the contracts now expect it.

## Parallel-agent sweep pattern

When the user explicitly wants broader recommendation coverage, use parallel subagents to split the search space before creating issues.

Recommended split:
1. Navigation/discoverability surfaces
   - Focus on `docs/document-intelligence/README.md`, `intelligence-accessibility-map.md`, `intelligence-accessibility-registry.yaml`, wiki indexes, and cross-link artifacts.
2. Source-ingest / batch-pack execution gaps
   - Focus on priority queues, staged batch packs, maturity ledgers, online-resource registries, and transfer ledgers.
3. Tacit-knowledge / repo-intelligence promotion gaps
   - Focus on closed issues, handoffs, review artifacts, WRK completion archives, and seed surfaces.

For each subagent:
- keep the task read-only
- require duplicate checks against open issues
- ask for 2-4 issue-ready candidates with labels, scope boundaries, and why they are not duplicates

Then, in the main context:
- synthesize the candidate list
- discard overlap-prone ideas
- keep the issues with the clearest ownership concern and strongest live evidence
- write body files and create the issues yourself so taxonomy/wording stay consistent

## Issue creation pattern

For each candidate issue:

1. Verify non-duplication with a targeted `gh issue list --search ...` query.
2. Pull 2-4 concrete facts from repo artifacts (counts, missing files, explicit gap statements in docs).
3. Write a temp markdown body file with these sections:
   - Summary
   - Why
   - Scope
   - Deliverables
   - Acceptance Criteria
   - Related
4. Prefer labels already in repo taxonomy:
   - `enhancement`
   - `priority:high|medium`
   - one category label such as `cat:data-pipeline`, `cat:documentation`, or `cat:harness`
   - one domain label such as `domain:document-intelligence` or `domain:knowledge-management`
5. Create with `gh issue create --body-file ...`
6. Immediately verify the created issue via `gh issue view --json number,title,url,labels,body`

## Writing heuristics

- Create issues that bridge existing architecture to missing implementation, not broad vague ideas.
- Reuse existing queue/plan artifacts when they already define a bounded execution slice.
- Prefer strengthening thin or weakly connected wiki domains over adding more volume to already-dense domains.
- Use live counts in the issue body when they justify prioritization.
- If an adjacent issue already exists but only covers a neighboring layer, create the new issue only if the ownership concern is clearly different.

## Additional proven issue themes from deeper recommendation sweeps

After the first gap-to-issues pass, the following additional themes also produced strong, non-duplicate issues when validated with parallel subagents:

1. Canonical marine-index repair
   - Examples: faceted portals, canonical index chunking/pagination, source-title aliasing.
   - Signals:
     - marine-engineering `wiki/index.md` is ~20k+ lines
     - source corpus dominates the domain
     - source-page titles are mostly filenames or numeric IDs
2. Batch-pack execution children beyond Pack 1
   - Examples: Batch Pack 2 indexed conference-summary promotion, Batch Pack 3 Tier A external engineering software profiles, Batch Pack 4 non-ACMA standards-summary promotion.
   - Important lesson: treat each pack as a separate issue only when the source family, execution mode, and duplicate boundaries are clean.
3. Policy-to-enforcement follow-ons
   - Examples: promotion audit-trail checker, GUARD-1 invented-layer detector, recurring-run output pruner, handoff expiration metadata.
   - Signals:
     - policy docs explicitly name future enforcement/checker surfaces
     - repo still contains live examples of the forbidden/unguarded pattern
4. Transient/tacit-knowledge routing substrates
   - Examples: transient-promotion candidate queue, closed-issue promotion ledger, WRK completions normalization, provenance backfill.
   - Signals:
     - repo already has handoffs/review artifacts/WRK archives, but no operational queue or normalized seed surface.
5. Registry-backed discoverability surfaces
   - Examples: task/asset explorer from accessibility registry, wiki-index uplink/back-navigation standard.
   - Signals:
     - navigation metadata exists in YAML/docs, but is not yet exposed as a generated explorer or standard nav surface.
6. Promotion-pipeline traceability plumbing
   - Example: thread `source_doc_key` through promoted artifacts alongside `content-hash`.
   - Signal:
     - contract explicitly distinguishes output integrity vs source traceability, but code still emits only integrity stamps.

## Roadmap / umbrella pattern

When the user wants to continue after multiple issue-creation waves, stop mining for more ideas and switch to execution-structure work.

Recommended next step after ~10+ grounded issues exist:
1. Read the created issues back with `gh issue view`.
2. Use parallel subagents to group them into:
   - provenance/governance/foundation
   - content-promotion/source-family execution
   - navigation/discoverability
3. Synthesize execution waves with:
   - hard prerequisites
   - soft sequencing preferences
   - safe parallel bundles (separate worktrees)
   - readiness mismatches discovered during review
4. Create one umbrella issue for roadmap/steering only.

A good umbrella issue should:
- list the child issues by wave
- record prerequisites like schema authority / `doc_key` / `promoted_from`
- note known readiness problems (for example, when a child issue's starter slice mismatches live repo data)
- stay planning-only; do not absorb implementation scope from child issues

## Do-not-file heuristics learned from this sweep

- Do not file a residual source-family issue if the remaining records collapse to a tiny, heterogeneous set after excluding overlap with already-filed batch packs.
- Do not create a navigation issue that overlaps with an existing portal/chunking issue unless the ownership concern is clearly different (for example, cross-wiki nav standard vs large-domain portal generation).
- Do not file broad provenance issues when the repo already has a parent contract issue and the real gap is a specific implementation child.
- When a recommendation depends on unresolved live-data readiness, either narrow the issue or record the mismatch explicitly in the body/roadmap instead of pretending the initial scope is execution-ready.

## Good example candidates

- `feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages`
- `feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains`
- `feat(knowledge): promote design-code registry into standards overviews and repo-target backlinks`
- `feat(knowledge): add llm-wiki strengthening scorecard and prioritized action queue`
- `feat(knowledge): generate faceted portal pages for large LLM-wiki domains`
- `feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs`
- `feat(knowledge): build transient-promotion candidate queue from handoffs and review artifacts`
- `feat(conformance): add promotion audit-trail checker for L5/L6→L3 wiki promotions`
- `feat(doc-intel): thread source_doc_key through promotion pipeline and promoted artifacts`
- `epic(knowledge): llm-wiki strengthening roadmap and execution waves`

## Pitfalls

- Do not create duplicates of umbrella/architecture issues when the real gap is an unexecuted child implementation.
- Do not rely on stale remembered wiki counts; count the current repo state.
- Do not pitch raw-source ingest work before checking whether metadata-first or summary-backed promotion is already designed.
- Do not create a generic "improve llm-wiki" issue when the repo already has specific artifacts that justify narrower, executable stories.
