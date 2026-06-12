---
name: project_graph_rag_assessment_llm_wiki_443
description: "Graph RAG assessment for repo ecosystem — issue llm-wiki#443 + Phase-1 deterministic-graph spike executed"
metadata: 
  node_type: memory
  type: project
  originSessionId: 26ba3eb2-ab0f-4f41-a2eb-cd9bcd325599
---

Graph RAG (graph-based RAG) assessment for the /mnt/local-analysis repo ecosystem. Created **llm-wiki#443** ("research(retrieval): Graph RAG assessment...") on 2026-06-07 — filed PRIVATE in llm-wiki (corpus internals) per [[feedback_porting_issues_private_not_public_hub]]. Links into existing web: #420 (storage epic, answers its Q4/Q6), #77 (graph manifests = bootstrap edges, plan-approved), #102 (validator hardening for #77), #13 (roadmap epic), #78 (RAG eval pattern), raw-to-knowledge-playbook#12 (public methodology counterpart).

**Research verdict (2025-26 survey):** LightRAG (MIT, true incremental insert) = top framework candidate for the cron-grown standards corpus; LazyGraphRAG for global sensemaking at ~0.1% index cost; HippoRAG2 for multi-hop. AVOID as hard deps: Neo4j Community (GPLv3 server), FalkorDB (SSPLv1), Kuzu (MIT but ARCHIVED Oct 2025, `ryugraph` fork). Two load-bearing findings: (1) code repos → build graph STRUCTURALLY via tree-sitter/AST, never LLM extraction (arXiv 2601.08773, RepoGraph ICLR 2025); (2) standards corpora → schema-first beats free extraction (Dagstuhl TGDK 2025); keep verified tables as typed nodes, never re-extract (fidelity regression per [[project_llm_wiki_table_fidelity_provisional]]). LLM extraction ≈ 75% of GraphRAG cost — biggest lever is using free deterministic edges.

**Phase-1 spike EXECUTED 2026-06-07** (results posted as #443 comment — durable record). Dependency-free stdlib script preserved at `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/graphrag-phase1-spike.py.txt` + report `graphrag-phase1-report.md` (since /tmp is ephemeral). Built standards citation graph from EXISTING structure, zero LLM cost: **305 nodes, 318 resolved standard→standard citation edges mined from page BODY text** (the existing `wiki-cross-links.py` only does fuzzy slug/title/tag, never reads body — misses this layer). 126-node giant component (41%) for free; 53% orphans (= deterministic layer necessary-but-not-sufficient, quantifies LLM-extraction need). Top hubs: api-510, iso-15156, api-rp-579, bs-7910. **Sleeper deliverable: ingestion-gap queue** = standards cited-but-not-in-corpus, ranked by mentions (iso-10423 @1327, iso-13628-7/-4/-5/-2 subpart family, asme-b31, iso-11960, iso-19902) → free acquisition list for the [[project_llm_wiki_corpus_ingest_cron]].

**KEY caveat (= a design requirement):** regex citation mining mis-parsed publication YEARS as ISO numbers (iso-2003@1327 from "ISO 19901-1:2009"); added year-filter heuristic but durable fix = resolve mentions against a curated standard-number REGISTRY, not raw regex.

**Corpus reality (verified, corrects an earlier subagent error that claimed domains empty):** 24,043 wiki .md pages; marine-engineering dominates with 21,117; 322 standard page-dirs / 297 distinct code_ids; 709 papers dirs. Nodes = standards page-dirs w/ frontmatter (code_id/publisher/revision/visibility/parse_status); landing files are `<rev>-full-text-part-NN.md`.

**Next step (checklisted on #443, NOT yet done — plan-review gated):** land spike as tested tool under `scripts/knowledge/` w/ registry-based resolution (TDD); extend nodes to papers/concepts; emit JSONL manifest aligned to #77 schema (spike `cite` edge = #77 `cites`); route gap queue to ingest cron. Did NOT commit (gate); repo left clean.
