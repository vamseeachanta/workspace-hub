# Plan for #2403: Embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2403
> **Review artifacts:** populated after cross-review dispatch

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/knowledge/llm_wiki.py` — wiki tokenization surface; no vector store.
- `scripts/data/doc_intelligence/` — 30+ pipeline scripts; target corpus producer.
- Prior art: `#1772` (CLOSED) — OCR + semantic search for 6 standards orgs (525 files); spike can borrow eval methodology.

### Standards
Not applicable.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — target L3 corpus sample.
- `knowledge/wikis/marine-engineering/wiki/index.md` — large index; representative of scale.

### Documents consulted
- Operating model §3 (`doc_key` identity) — eval set uses `doc_key` as ground-truth reference.
- `#2402` (OPEN) — downstream build issue that consumes this spike's decision.
- Memory `project_hermes_codex_quota.md` — cost sensitivity context.

### Dependency Matrix

| Issue | State | Relationship | Behavior |
|---|---|---|---|
| #2402 | OPEN | **consumes this spike's decision** | #2402 blocks on this |
| #1772 | CLOSED | prior art | methodology reference only |

### Gaps identified
- No eval set exists for our corpus.
- No comparison methodology.
- No cost/latency/recall baseline.

### Evidence (embedded verification)

**Issue statuses** (2026-04-20T16:10Z):
- `#2403` OPEN — this issue
- `#2402` OPEN — downstream consumer
- `#1772` CLOSED — prior art

**File existence:**
```
EXISTS: scripts/knowledge/llm_wiki.py
EXISTS: scripts/data/doc_intelligence/ (30+ files)
EXISTS: knowledge/wikis/engineering/wiki/index.md
EXISTS: knowledge/wikis/marine-engineering/wiki/index.md
MISSING (new): tests/fixtures/embeddings/eval-set.jsonl
MISSING (new): scripts/knowledge/run_embeddings_spike.py
MISSING (new): docs/document-intelligence/embeddings-model-selection.md
```

Distinct sources: **9**.

---

## Cross-Machine Tier Assignment (§7)

| Artifact | Path | Tier | Authority |
|---|---|---|---|
| Eval set | `tests/fixtures/embeddings/eval-set.jsonl` | 1 git-tracked | authoritative |
| Spike runner | `scripts/knowledge/run_embeddings_spike.py` | 1 git-tracked | authoritative |
| Decision doc | `docs/document-intelligence/embeddings-model-selection.md` | 1 git-tracked | authoritative |
| Measurement outputs (per run) | `docs/reports/embeddings-spike/<model>-<ts>.json` | 1 git-tracked | evidence for decision |
| Optional: raw embedding vectors (spike only, throwaway) | `/tmp/embeddings-spike/*.npy` | 3 local-cache | throwaway |

---

## Threat Model

**Input surfaces:** text from wiki pages + registry summaries.
**Trust boundaries:** corpus is git-tracked (trusted). Model endpoints (Voyage, OpenAI) are external; secrets required.
**Mitigations:**
- API keys loaded from environment variables only; never committed.
- Spike cost cap: `SPIKE_MAX_USD` env var (default $5); script exits if projected cost exceeds cap.
- Local BGE-M3 run requires no secrets (Ollama-local).
- Eval set content reviewed before commit (human-curated; ≥50 queries).

**Tests:**
- `test_spike_aborts_over_cost_cap`
- `test_spike_rejects_uncurated_eval_set` (fail if <50 queries)
- `test_api_keys_loaded_from_env_only`

---

## AC ↔ Test Map

| AC | Test(s) |
|---|---|
| Eval set exists at fixture path | `test_eval_set_exists_with_50_plus_queries` |
| Spike runner produces per-model measurement JSON | `test_spike_runner_produces_json_per_model` |
| Cost cap honored | `test_spike_aborts_over_cost_cap` |
| API keys env-loaded | `test_api_keys_loaded_from_env_only` |
| Decision doc written with all 3 models + chosen pick | `test_decision_doc_contains_all_models_and_pick` |
| Decision doc references measurement commit SHA | `test_decision_doc_references_commit_sha` |
| Decision justified by numbers in the doc | reviewer-task (not automated) |

---

## Deliverable

A reproducible spike that:
1. Curates a ≥50-query eval set with known-good `doc_key` targets drawn from current L2 summaries + L3 wiki pages.
2. Runs each of 3 candidate models (BGE-M3 local, Voyage-3 cloud, text-embedding-3-large cloud) against the eval set.
3. Measures recall@10, $/1000-doc-build, p95 query latency.
4. Writes `docs/document-intelligence/embeddings-model-selection.md` with rubric + numbers + decision + rationale.

---

## Pseudocode

```python
# scripts/knowledge/run_embeddings_spike.py
def main():
    eval_set = load_jsonl("tests/fixtures/embeddings/eval-set.jsonl")
    assert len(eval_set) >= 50, "eval set must have >=50 queries"

    models = [
        ("bge-m3-local", run_bge_m3_via_ollama),
        ("voyage-3-cloud", run_voyage),
        ("text-embedding-3-large", run_openai),
    ]

    for name, runner in models:
        check_cost_budget_or_abort(name)
        result = {
            "model": name,
            "corpus_docs_embedded": 0,
            "cost_usd": 0,
            "recall_at_10": 0,
            "p95_latency_ms": 0,
        }
        # Embed corpus sample
        t0 = time.time()
        corpus_vecs = [runner(doc.text) for doc in corpus_sample(n=500)]
        result["corpus_docs_embedded"] = len(corpus_vecs)
        result["cost_usd"] = runner.cost_tally
        # Evaluate recall
        hits = 0
        latencies = []
        for q in eval_set:
            t_start = time.time()
            q_vec = runner(q.query_text)
            results = cosine_topk(q_vec, corpus_vecs, k=10)
            latencies.append(time.time() - t_start)
            if q.target_doc_key in [r.doc_key for r in results]:
                hits += 1
        result["recall_at_10"] = hits / len(eval_set)
        result["p95_latency_ms"] = percentile(latencies, 95) * 1000
        write_json(f"docs/reports/embeddings-spike/{name}-{ts}.json", result)

    render_decision_doc()  # compile all 3 results + pick winner
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/run_embeddings_spike.py` | spike runner |
| Create | `tests/fixtures/embeddings/eval-set.jsonl` | ≥50 curated queries |
| Create | `tests/knowledge/test_embeddings_spike.py` | TDD suite |
| Create | `docs/reports/embeddings-spike/` | per-model measurement outputs dir |
| Create | `docs/document-intelligence/embeddings-model-selection.md` | decision doc |

---

## Acceptance Criteria

- [ ] Eval set at `tests/fixtures/embeddings/eval-set.jsonl` with ≥50 queries, each with target `doc_key`
- [ ] Spike runner executes all 3 models end-to-end on ≥500-doc corpus sample
- [ ] Per-model JSON output committed to `docs/reports/embeddings-spike/`
- [ ] Decision doc compiled with rubric + numbers + chosen pick + 2-sentence rationale
- [ ] Cost cap enforced (test + empirically respected during spike)
- [ ] Review artifacts posted

---

## Risks and Open Questions

- **Risk:** Voyage + OpenAI cost could exceed $5 cap on full corpus. Mitigation: sample N=500 (not full corpus); cap enforced pre-run.
- **Risk:** BGE-M3 local inference requires Ollama install + GPU/CPU capacity. Mitigation: spike runs on dev-primary; fall back to CPU with documented latency caveat.
- **Open:** Should eval set be hand-curated by domain expert, or synthetic from wiki page titles? Plan: seed with 25 synthetic + 25 hand-picked from existing issue corpus to get balanced coverage.
- **Open:** Include re-ranker (e.g., Cohere Rerank) in comparison? Plan: out of scope for v1; follow-on if retrieval quality bottleneck post-#2402.

---

## Complexity: T2
