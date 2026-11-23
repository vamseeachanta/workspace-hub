# Plan for #2393: Embeddings index over L2 registry + L3 wiki pages (nightly refresh)

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2393
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2393-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — tokenizes wiki content but no vector store.
- Found (closed): #1772 built an OCR + semantic-search index for 6 standards orgs (525 files) — scope was narrow; code may be salvageable.
- Found: `scripts/data/document-index/phase-a-index.py` — extracts summaries we'll embed.
- Gap: no embedding store, no query CLI, no corpus-wide semantic search over L2+L3.

### Standards
Not applicable — tooling issue.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — target L3 corpus (sample); varying frontmatter shape per §8.1.
- `knowledge/wikis/marine-engineering/wiki/index.md` — large index, motivates chunking (#2378 is paginating this).

### Documents consulted
- Operating model §3 (`doc_key` identity — embeddings keyed on doc_key), §7 (cross-machine tier rules — Parquet blob may live on `/mnt/ace/`, manifest must be git-tracked).
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` §4 flows — confirms embeddings are a *derived* L2/L3 artifact (not a new layer).
- Related issue #2360 — wiki `doc_key` is the join key; embeddings build is unreliable until #2360 ships OR tool handles missing keys.
- Related issue #2363 (wiki_refs reverse lookup) — complementary retrieval path.
- Related issue #1772 (closed) — prior art for semantic search.
- Memory `project_hermes_codex_quota.md` — cost guardrails matter; plan must enforce budget envelope.

### Gaps identified
- No embedding model selection — spike required.
- No vector store chosen — Parquet+DuckDB vs. SQLite vs. in-memory FAISS.
- No chunking strategy — wiki pages vary from 500 to 50,000 tokens.

**Distinct sources consulted: 9** — exceeds ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2393-embeddings-index-l2-l3.md` |
| Spike: model selection | `docs/document-intelligence/embeddings-model-selection.md` |
| Index build | `scripts/knowledge/build_embeddings_index.py` |
| Query CLI | `scripts/knowledge/query_embeddings.py` |
| Manifest (git-tracked) | `data/document-index/embeddings-manifest.yaml` |
| Storage (gitignored) | `data/document-index/embeddings.parquet` → cache mirror at `/mnt/ace/.embeddings/` |
| Tests | `tests/knowledge/test_embeddings_index.py` |
| Cron wiring | `config/scheduled-tasks/schedule-tasks.yaml` |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2393-claude.md` |

---

## Deliverable

A nightly-refreshed vector index `data/document-index/embeddings.parquet` covering L2 summaries + L3 wiki chunks, addressable by `doc_key`, queryable via `query_embeddings.py --text "…" --top-k N --layer L2|L3|both`.

---

## Pseudocode

```
# Stage 0 — model-selection spike (separate deliverable)
compare: BGE-M3 (local, Ollama) vs Voyage-3 vs text-embedding-3-large
metrics: recall@10 on synthetic eval set (50 queries, known-good targets), $/1K docs, p95 latency
decide → write docs/document-intelligence/embeddings-model-selection.md

# Stage 1 — build
function build_index():
    load L2 summaries from phase-a-index + registry
    load L3 chunks from knowledge/wikis/**/*.md
        chunking: semantic-break at ## headers, max-tokens=512, overlap=64
    for each unit (doc_key, chunk_id, text):
        if unchanged_since_last_run(chunk_hash):
            reuse cached embedding
        else:
            embed(text, model=CHOSEN_MODEL)
            record cost/tokens
    write parquet (doc_key, chunk_id, chunk_hash, vector, layer, path)
    write embeddings-manifest.yaml (model, version, row_count, refresh_ts, cost)

# Stage 2 — query
function query(text, top_k, layer_filter):
    q_vec = embed(text, model=MANIFEST.model)
    results = parquet.cosine_similarity(q_vec, vectors, top_k)
    return [{doc_key, chunk_id, path, similarity, excerpt}]

# Stage 3 — nightly refresh
cron: scripts/knowledge/build_embeddings_index.py --incremental
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/build_embeddings_index.py` | Build + incremental refresh |
| Create | `scripts/knowledge/query_embeddings.py` | Query CLI |
| Create | `scripts/knowledge/embeddings/__init__.py` | Shared helpers |
| Create | `scripts/knowledge/embeddings/chunker.py` | Semantic chunking |
| Create | `scripts/knowledge/embeddings/models.py` | Pluggable embedding-model interface |
| Create | `tests/knowledge/test_embeddings_index.py` | TDD tests |
| Create | `tests/knowledge/fixtures/embeddings/` | Small canned corpus |
| Create | `data/document-index/embeddings-manifest.yaml` | Git-tracked manifest |
| Create | `docs/document-intelligence/embeddings-model-selection.md` | Spike deliverable |
| Modify | `.gitignore` | Ignore `data/document-index/embeddings.parquet` + local cache |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Nightly refresh entry |
| Update | `docs/plans/README.md` | Add this plan |

---

## TDD Test List

| Test | Verifies | Input | Expected |
|---|---|---|---|
| test_chunker_respects_semantic_breaks | Chunks split on `##` headers, never mid-sentence | 3-heading markdown | 3 chunks aligned to headers |
| test_chunker_max_token_cap | Chunks never exceed max_tokens+overlap | 10K-token input | all chunks ≤ 576 tokens |
| test_build_creates_manifest | Fresh build writes manifest with required fields | empty corpus dir | manifest has model, version, row_count=0, refresh_ts |
| test_build_is_incremental | 2nd build reuses unchanged chunks | 100 docs, change 1 | only 1 embed call beyond first run |
| test_query_returns_top_k | Query returns exactly K results sorted | 5-doc corpus, k=3 | 3 results, descending similarity |
| test_query_layer_filter | `--layer L3` excludes L2 entries | mixed corpus | only L3 results |
| test_manifest_model_pin | Query fails if manifest model ≠ runtime model | manifest says X, CLI uses Y | exit code ≠0, clear error |
| test_cost_log_captured | Build records token count + cost in manifest | 10-doc build | manifest.cost > 0 |
| test_missing_doc_key_skipped | L3 pages lacking `doc_key` frontmatter excluded cleanly | mixed corpus | log + skipped-count field in manifest |
| test_parquet_gitignored | `.gitignore` includes embeddings.parquet | — | grep .gitignore succeeds |

---

## Acceptance Criteria

- [ ] Stage-0 spike lands as `docs/document-intelligence/embeddings-model-selection.md` with rubric + decision
- [ ] All tests pass: `uv run pytest tests/knowledge/test_embeddings_index.py -v`
- [ ] First real run writes `embeddings-manifest.yaml` with ≥1000 rows on current corpus
- [ ] Query latency p95 < 2s on local corpus
- [ ] Nightly cron entry merged
- [ ] `.gitignore` updated to exclude `embeddings.parquet` blob
- [ ] Review artifacts posted

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self) | MINOR | See findings A–D below |
| Codex | PENDING | Recommended before approval given cost implications |
| Gemini | PENDING | Optional |

Revisions made inline based on self-review:
- **A:** Added `test_manifest_model_pin` — prevents silently querying with different model than built with.
- **B:** Added explicit chunk-hash caching in pseudocode (was ambiguous about incremental refresh behavior).
- **C:** Added `.gitignore` as a Files-to-Change row + corresponding test (was mentioned in AC but not wired).
- **D:** Added `test_missing_doc_key_skipped` — must not crash on pre-#2360 wiki state.

---

## Risks and Open Questions

- **Risk:** Embedding cost overrun if model selection defaults to cloud model + corpus grows. Mitigation: manifest records cost, cron aborts if nightly cost >$5 without `--force`.
- **Risk:** Wiki `doc_key` coverage low until #2360 lands. Mitigation: tool skips missing keys with logging; index rebuild scheduled after #2360 completes.
- **Risk:** Chunking mid-table or mid-code-block degrades retrieval. Mitigation: chunker has semantic-break rules; tests cover markdown structures.
- **Open:** Single global index vs. per-domain index? Start with single; revisit if query latency degrades.

---

## Complexity: T3

Multi-stage (spike + build + query + cron), multi-file, new vector-store paradigm.
