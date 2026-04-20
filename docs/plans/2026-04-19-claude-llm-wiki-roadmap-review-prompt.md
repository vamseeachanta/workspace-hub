# Claude review prompt — LLM-wiki strengthening roadmap and issue portfolio

Use this prompt as-is for Claude to review the current LLM-wiki strengthening work in `workspace-hub`.

---

You are conducting an adversarial review of the current LLM-wiki strengthening portfolio in the `workspace-hub` repository.

Repository
- Path: `/mnt/local-analysis/workspace-hub`
- GitHub repo: `vamseeachanta/workspace-hub`

Primary objective
- Review the issue portfolio, roadmap, dependencies, scope boundaries, and execution sequencing for the current LLM-wiki strengthening wave.
- Your job is to find what is wrong, overlapping, missing, risky, or incorrectly sequenced.

Review stance requirements
1. You are an adversarial reviewer. Assume the roadmap and issue set have defects until proven otherwise.
2. Do not praise.
3. Do not restate issue bodies unless needed to cite a problem.
4. Focus on dependency errors, duplicate work, incorrect scoping, missing prerequisites, readiness mismatches, and execution risk.
5. Return APPROVE only if you can affirmatively verify that the portfolio is well-structured and execution-ready.
6. If uncertain, return MINOR or MAJOR.
7. Every finding must cite issue numbers and, where useful, specific files or dependency relationships.
8. Treat all claims in issue bodies and the umbrella roadmap as assertions to verify, not facts to trust.

Core umbrella to review
- #2390 `epic(knowledge): llm-wiki strengthening roadmap and execution waves`

Issue portfolio in scope

1) Provenance / governance / data foundation
- #2363 `feat(doc-intel): materialize wiki_refs reverse lookup from doc_key to citing wiki pages`
- #2371 `feat(knowledge): backfill promotion provenance on pre-existing wiki pages`
- #2382 `feat(conformance): add promotion audit-trail checker for L5/L6→L3 wiki promotions`
- #2383 `feat(conformance): implement GUARD-1 invented-layer detector for intelligence/governance docs`
- #2374 `feat(knowledge): build transient-promotion candidate queue from handoffs and review artifacts`
- #2375 `feat(knowledge): normalize WRK completions into structured seeds and wiki-candidate corpus`
- #2381 `chore(governance): add computable expiration metadata to session handoffs`
- #2384 `feat(governance): add promotion-aware recurring-run output pruner`
- #2389 `feat(doc-intel): thread source_doc_key through promotion pipeline and promoted artifacts`

2) Promotion waves / content expansion
- #2364 `feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains`
- #2369 `feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs`
- #2373 `feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion`
- #2380 `feat(knowledge): execute Batch Pack 3 Tier A for external engineering software profiles`
- #2365 `feat(knowledge): promote design-code registry into standards overviews and repo-target backlinks`

3) Navigation / discoverability
- #2366 `feat(knowledge): add llm-wiki strengthening scorecard and prioritized action queue`
- #2368 `feat(knowledge): generate faceted portal pages for large LLM-wiki domains`
- #2372 `feat(knowledge): add canonical source-title aliasing for wiki source pages`
- #2378 `feat(knowledge): chunk and paginate the canonical marine-engineering wiki index`
- #2379 `feat(knowledge): generate task and asset explorer views from the intelligence accessibility registry`
- #2388 `docs(knowledge): add standard uplink/back-navigation block to wiki index pages`

Important adjacent prerequisites / related issues to verify against
- #2205 operating model
- #2206 conformance umbrella
- #2207 provenance/reuse contract
- #2209 durable-vs-transient boundary
- #2137 canonical intelligence entry points
- #2242 priority queue
- #2243 staged batch packs
- #2360 wiki CLAUDE.md require doc_key
- #2233 promoted_from frontmatter guidance
- #2362 back-populate doc_key on pre-existing standards-transfer-ledger entries
- #2236 post-closure promotion workflow
- #2237 cleanup/archive automation
- #2238 closed-issue citation guardrail

Files you should inspect directly
Roadmap / architecture / governance
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/pyramid-conformance-checks.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/document-intelligence/README.md`

Queue / execution design
- `docs/reports/llm-wiki-external-source-priority-queue.md`
- `docs/reports/llm-wiki-staged-batch-packs.md`
- `docs/reports/2026-04-16-llm-wiki-resource-intelligence-unified-review.md`

Representative data / implementation surfaces
- `data/document-index/intelligence-accessibility-registry.yaml`
- `data/document-index/resource-intelligence-maturity.yaml`
- `data/document-index/online-resource-registry.yaml`
- `data/design-codes/code-registry.yaml`
- `knowledge-base/wrk-completions.jsonl`
- `knowledge/wikis/marine-engineering/wiki/index.md`
- `knowledge/wikis/engineering/wiki/index.md`
- `scripts/knowledge/llm_wiki.py`
- `scripts/data/doc_intelligence/promoters/`
- `scripts/data/doc_intelligence/promoters/coordinator.py`
- `scripts/data/doc_intelligence/orchestrator.py`

Specific review questions
1. Are any of the current issues duplicates or near-duplicates that should be merged?
2. Are any issues too broad and should be split before planning/execution?
3. Are any issues too narrow and should be absorbed into another issue?
4. Are the dependency edges in #2390 materially correct?
5. Are any prerequisites missing from #2390?
6. Is any issue placed in the wrong wave?
7. Are any issues sequenced too late or too early?
8. Is the current provenance/governance ordering correct, especially around:
   - #2363
   - #2371
   - #2382
   - #2389
   - #2374
   - #2384
9. Is the navigation ordering correct, especially around:
   - #2372
   - #2368
   - #2378
   - #2379
   - #2388
10. Is #2369 still mismatched with live repo readiness if the issue body names DOT/OMAE/ISOPE but repo state indicates DOT/OMAE/OTC as phase-A complete?
11. Are #2365 and #2373 adequately separated, or do they still overlap too much around standards-family promotion?
12. Is #2380 properly scoped relative to #2364, #2039, and #2042?
13. Are #2374, #2375, #2381, and #2384 sequenced correctly relative to one another?
14. Are there any missing execution-risk notes around shared write surfaces, worktree contention, or duplicated regeneration of wiki/index/navigation artifacts?

Required output format

## 1. Verdict
- APPROVE / MINOR / MAJOR

## 2. Critical findings
- Bullet list
- Each bullet must cite issue numbers and the specific defect

## 3. Dependency corrections
- Use format: `Issue A should precede/follow Issue B because ...`

## 4. Merge / split recommendations
- Explicit issue numbers
- Be concrete about whether to merge, split, or tighten scope only

## 5. Scope fixes
- Titles and/or issue bodies that should be tightened before planning/execution

## 6. Readiness mismatches
- Any issue whose described scope does not match live repo state

## 7. Revised first-wave recommendation
- Give the best first execution wave after considering all findings
- Keep it concise and actionable

Important constraints
- Do not suggest implementation work outside the issue portfolio unless a missing prerequisite is genuinely necessary.
- Prefer tightening scope over inventing new work.
- If you think #2390 should be patched, say exactly what should change.

---

Suggested one-line ask to Claude

Please adversarially review #2390 and its linked issue portfolio using the instructions above. Focus on dependency correctness, duplicate risk, readiness mismatches, and whether the first execution waves are sequenced correctly.
