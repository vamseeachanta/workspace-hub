# LLM-wiki strengthening issue-discovery exit handoff

Date: 2026-04-20T10:08:11-05:00
Repo: `/mnt/local-analysis/workspace-hub`
Mode: issue discovery, dependency synthesis, roadmap creation, Claude handoff prep

## Session summary

This session focused on reviewing the `workspace-hub` repo ecosystem, identifying LLM-wiki strengthening opportunities, creating the corresponding GitHub issues, and then moving from issue discovery into roadmap/dependency organization.

Work completed:
- reviewed repo/document/wiki ecosystem with repeated grounded searches and live GitHub duplicate checks
- created a large linked issue set for llm-wiki strengthening
- created an umbrella roadmap/epic issue with execution waves and dependency notes
- prepared a comprehensive Claude review prompt in-repo for external adversarial review
- posted a review packet comment on the umbrella issue for easy handoff/reference

## Key artifacts created this session

### Umbrella roadmap
- GitHub issue: `#2390` `epic(knowledge): llm-wiki strengthening roadmap and execution waves`
- Purpose: dependency grouping, execution waves, parallelization notes, readiness caveats

### Claude handoff prompt
- File: `docs/plans/2026-04-19-claude-llm-wiki-roadmap-review-prompt.md`
- Purpose: comprehensive adversarial review packet for Claude over `#2390` and linked child issues

### Claude review packet comment
- GitHub comment on `#2390`:
  `https://github.com/vamseeachanta/workspace-hub/issues/2390#issuecomment-4281940796`

## Issue portfolio created/curated in this workstream

### Provenance / governance / data foundation
- `#2363` wiki_refs reverse lookup
- `#2371` provenance backfill on pre-existing wiki pages
- `#2382` promotion audit-trail checker
- `#2383` GUARD-1 invented-layer detector
- `#2374` transient-promotion candidate queue
- `#2375` WRK completions normalization
- `#2381` handoff expiration metadata
- `#2384` recurring-run output pruner
- `#2389` source_doc_key threading through promotion pipeline

### Promotion waves / content expansion
- `#2364` Batch Pack 1 API/standards-portal metadata promotion
- `#2369` Batch Pack 2 indexed conference-summary promotion
- `#2373` Batch Pack 4 non-ACMA standards-summary promotion
- `#2380` Batch Pack 3 Tier A external engineering software profiles
- `#2365` design-code registry promotion

### Navigation / discoverability
- `#2366` strengthening scorecard
- `#2368` large-domain portal pages
- `#2372` source-title aliasing
- `#2378` canonical marine-engineering index chunking/pagination
- `#2379` registry/task explorer
- `#2388` wiki index uplink/back-navigation standard

## Recommended execution order snapshot

### Wave 0 — prerequisites / schema authority
These were identified as practical prerequisites, though not created in this session:
- `#2360` require `doc_key` in wiki CLAUDE.md files
- `#2233` promoted_from guidance
- `#2362` back-populate doc_key on old standards-transfer-ledger entries

### Wave 1 — low-risk provenance and guardrail foundations
- `#2383`
- `#2389`
- `#2363`

### Wave 2 — legacy provenance + transient metadata
- `#2371`
- `#2381`

### Wave 3 — transient intake / candidate extraction
- `#2374`
- `#2375`

### Wave 4 — governance enforcement / cleanup
- `#2382`
- `#2384`

### Wave 5 — first promotion-family execution
- `#2364`
- `#2365`

### Wave 6 — next promotion-family execution
- `#2380`
- `#2369` after readiness correction

### Wave 7 — broader standards-summary promotion
- `#2373`

### Wave 8 — navigation / discoverability
- `#2372`
- `#2366`
- `#2368` + `#2379`
- `#2378`
- `#2388`

## Important readiness caveat

### #2369 scope mismatch
Parallel dependency review found that `#2369` currently describes DOT/OMAE/ISOPE as the phase-A-complete starter collections, while repo-state review indicated DOT/OMAE/OTC are phase-A complete and ISOPE is not yet indexed.

Recommended next action before execution:
- reconcile the issue body or post a corrective comment on `#2369`

## Recommended next actions for the next session

1. Send `docs/plans/2026-04-19-claude-llm-wiki-roadmap-review-prompt.md` to Claude for adversarial review
2. Patch `#2390` if Claude finds dependency or sequencing defects
3. Reconcile `#2369` readiness mismatch before planning/execution
4. Start planning Wave 1 first:
   - `#2383`
   - `#2389`
   - `#2363`
5. Treat `#2360`, `#2233`, and `#2362` as practical prerequisite gates in any execution plan

## Notes on what not to do next

- do not keep mining for more llm-wiki issues unless Claude review reveals a real gap
- do not start navigation polish (`#2368`, `#2378`, `#2388`) before source-title/provenance groundwork is stable
- do not execute `#2369` without fixing its collection-readiness mismatch
- do not prune recurring outputs (`#2384`) before transient-promotion intake surfaces (`#2374`) exist

## Exit status

Session is documented and ready for handoff.
Primary handoff artifact for Claude review:
- `docs/plans/2026-04-19-claude-llm-wiki-roadmap-review-prompt.md`
