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

## Good example candidates

- `feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages`
- `feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains`
- `feat(knowledge): promote design-code registry into standards overviews and repo-target backlinks`
- `feat(knowledge): add llm-wiki strengthening scorecard and prioritized action queue`

## Pitfalls

- Do not create duplicates of umbrella/architecture issues when the real gap is an unexecuted child implementation.
- Do not rely on stale remembered wiki counts; count the current repo state.
- Do not pitch raw-source ingest work before checking whether metadata-first or summary-backed promotion is already designed.
- Do not create a generic "improve llm-wiki" issue when the repo already has specific artifacts that justify narrower, executable stories.
