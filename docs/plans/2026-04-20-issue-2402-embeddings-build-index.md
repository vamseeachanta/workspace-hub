# Plan for #2402: Build embeddings index L2+L3 + query CLI (single authoritative tier)

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2402
> **Review artifacts:** populated after cross-review dispatch
> **Carries forward:** lessons from closed #2393 (3-iteration review cycle surfaced single-storage-authority, sha256 enforcement, p95-test-not-reviewer-task, cost-cap-with-impl, secret-management defects).

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/doc_intelligence/` — existing ingest pipeline directory (30+ files; this plan lives here per #2395 v3 namespace correction).
- `scripts/data/document-index/phase-a-index.py:135-137` — legacy md5 prefix handling for `og_standards` (embeddings build must tolerate).
- `scripts/knowledge/llm_wiki.py` — wiki ingest surface (read-only for indexing).
- Gap: no embedding store; no query CLI; confirmed via `Glob "**/embeddings*"` = 0 matches.

### Standards
Not applicable (tooling).

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — target L3 corpus sample.
- `knowledge/wikis/marine-engineering/wiki/index.md` — larger index; p95-latency-relevant scale.

### Documents consulted
- Operating model §3 (`doc_key` identity — index keyed on `doc_key`), §7 (tier rules — single authority).
- `docs/plans/2026-04-20-issue-2403-embeddings-model-selection-spike.md` — upstream spike providing model decision.
- `docs/plans/2026-04-20-issue-2393-embeddings-index-l2-l3.md` — closed predecessor (all findings addressed below).

### Dependency Matrix

| Issue | State | Relationship | Behavior if unshipped |
|---|---|---|---|
| #2403 | OPEN status:plan-approved | **HARD** (model must be chosen) | implementation waits |
| #2360 | OPEN status:plan-review | soft | tool tolerates missing `doc_key` via skipped-count |
| #2361 | OPEN | soft | tolerant |
| #2362 | OPEN | soft | tolerant |
| #2405 | OPEN status:plan-approved | soft (review-infra) | doesn't block implementation |

### Gaps identified
- No embedding-build module.
- No query CLI.
- No nightly refresh cron.
- No cost-cap implementation (v1 #2393 had prose mitigation without code).

### Evidence (embedded verification)

**Issue statuses** (via `gh issue view` 2026-04-20T16:50Z):
- `#2402` — OPEN `status:plan-approved` — this issue
- `#2403` — OPEN `status:plan-approved` — model-selection spike (hard-dep)
- `#2360` — OPEN — wiki CLAUDE.md doc_key requirement
- `#2405` — OPEN `status:plan-approved` — review-infra meta

**File existence** (`ls -la` 2026-04-20T16:50Z):
```
EXISTS: scripts/data/doc_intelligence/ (30+ files)
EXISTS: scripts/data/document-index/phase-a-index.py
EXISTS: scripts/knowledge/llm_wiki.py
EXISTS: knowledge/wikis/engineering/wiki/index.md
EXISTS: knowledge/wikis/marine-engineering/wiki/index.md
MISSING (new): scripts/knowledge/build_embeddings_index.py
MISSING (new): scripts/knowledge/query_embeddings.py
MISSING (new): data/document-index/embeddings-manifest.yaml
```

**Gap proof:** `Glob "**/embeddings*"` = 0 matches (2026-04-20) confirms no existing embedding infrastructure.

Distinct sources: **10**.

---

## Identity Contract (§3)

All indexed entries use `doc_key = sha256:<hex>` per §3. Legacy `md5:<hex>` accepted for reads only (compatibility with `og_standards` legacy entries per `phase-a-index.py:135-137`). Bare-hex rejected at index time. Path-only identity forbidden.

Index schema binds each vector to `(doc_key, chunk_id, chunk_hash, vector)`. Missing `doc_key` entries logged + skipped; counts surface in manifest.

Tests:
- `test_index_accepts_sha256_doc_keys`
- `test_index_accepts_md5_legacy_read_only`
- `test_index_rejects_bare_hex_doc_keys`
- `test_index_skips_missing_doc_key_with_count_in_manifest`

---

## Cross-Machine Tier Assignment (§7 — v1 #2393 two-copy bug addressed)

**Single authority decision: tier-1 git-tracked manifest + tier-3 local-cache blob.**

| Artifact | Path | Tier | Authority | Sync direction |
|---|---|---|---|---|
| Manifest | `data/document-index/embeddings-manifest.yaml` | **1 git-tracked** | **authoritative** | — |
| Vector blob | `data/document-index/embeddings.parquet` | 3 local-cache | **not authoritative** | gitignored; rebuildable from L2+L3 |
| Query CLI | `scripts/knowledge/query_embeddings.py` | 1 git-tracked | authoritative | — |
| Build script | `scripts/knowledge/build_embeddings_index.py` | 1 git-tracked | authoritative | — |
| Cost-log | `logs/embeddings-spike/<ts>.jsonl` | 3 local-cache | audit | — |

**No second copy on shared mount.** v1 #2393 had a fatal two-copy ambiguity (repo parquet + `/mnt/ace/.embeddings/`); v2 removes it. If per-machine reuse is desired, that's a follow-on issue with explicit sync semantics.

---

## Threat Model

**Input surfaces:** L2 yaml registries (git-tracked, trusted), L3 markdown files (git-tracked, trusted), model API endpoints (external).
**Trust boundaries:**
- Cloud embedding API (Voyage/OpenAI) — requires secret (env var), never committed.
- Local Ollama (BGE-M3) — no external secret surface if chosen by #2403.
- Chunk content is git-tracked — trusted.

**Mitigations:**
- Secrets: `VOYAGE_API_KEY` / `OPENAI_API_KEY` env-only. Never persisted to disk or logs. Test verifies no API key appears in manifest / logs / git-tracked files.
- Cost cap: `BUILD_MAX_USD` env var (default $5). Script aborts if projected cost exceeds cap; **tested with fixture that triggers abort**.
- API endpoint validation: only approved hostnames in allowlist (`api.openai.com`, `api.voyageai.com`, or localhost for Ollama).
- Stale manifest: build fails if manifest `model` field doesn't match runtime model — prevents garbage-similarity queries (was v1 #2393's `test_manifest_model_pin`).

**Threat tests:**
- `test_api_key_never_appears_in_manifest_or_log`
- `test_cost_cap_aborts_before_api_call`
- `test_endpoint_allowlist_enforced`
- `test_manifest_model_mismatch_aborts_query`

---

## AC ↔ Test Map

| AC | Test(s) |
|---|---|
| Build script produces manifest with required fields | `test_build_creates_manifest_with_model_version_count_timestamp` |
| Query CLI returns top-K results with similarity scores | `test_query_returns_top_k_sorted_with_similarity` |
| Row count ≥1000 on first real run | `test_build_emits_row_count_matching_corpus_sample` (fixture-based + logged expected-range) |
| p95 latency < 2s | `test_query_p95_under_2s_on_fixture_corpus` (NEW — automated benchmark, not reviewer-task) |
| Nightly cron entry | `test_cron_config_parses_and_schedules_nightly` |
| Cost cap enforced | `test_cost_cap_aborts_before_api_call` (from Threat Model) |
| Secrets never leaked | `test_api_key_never_appears_in_manifest_or_log` |
| sha256 enforcement | listed under Identity Contract |
| Model-pin invariant | `test_manifest_model_mismatch_aborts_query` |
| Single authority verified | `test_gitignore_excludes_parquet_blob` + `test_manifest_is_git_tracked` |
| Missing doc_key skip | `test_index_skips_missing_doc_key_with_count_in_manifest` |

---

## Deliverable

A `build_embeddings_index.py` + `query_embeddings.py` pair that produces a nightly-refreshed embeddings index keyed on `doc_key` over L2 summaries + L3 wiki chunks, with single-authority manifest (git-tracked) + local-cache Parquet blob (gitignored), cost-cap enforcement, secret-safety, and automated p95-latency/model-pin/sha256 invariants.

---

## Pseudocode

```python
# scripts/knowledge/build_embeddings_index.py
import os, yaml, hashlib, re, time
from pathlib import Path

SHA256_RE = re.compile(r"^sha256:[0-9a-f]+$")
MD5_RE = re.compile(r"^md5:[0-9a-f]+$")
ALLOWED_ENDPOINTS = {"api.openai.com", "api.voyageai.com", "localhost"}

def main():
    manifest_path = "data/document-index/embeddings-manifest.yaml"
    parquet_path = "data/document-index/embeddings.parquet"
    model_name = pick_model_from_2403_decision()
    budget_usd = float(os.environ.get("BUILD_MAX_USD", "5.0"))
    cost_to_date = 0.0

    # Load corpus
    entries = []
    for l2_yaml in [list_of_registries]:
        for row in load_yaml(l2_yaml):
            if row.doc_key is None:
                skip_log.append({doc: row.path, reason: "missing-doc-key"})
                continue
            if SHA256_RE.match(row.doc_key) or MD5_RE.match(row.doc_key):
                entries.append(row)
            else:
                raise ValueError(f"non-conforming doc_key in {row.path}: {row.doc_key}")

    for wiki in glob("knowledge/wikis/*/wiki/**/*.md"):
        fm = parse_frontmatter(wiki)
        if fm.get("doc_key") is None:
            skip_log.append({doc: wiki, reason: "missing-doc-key-§8.1"})
            continue
        for chunk in chunk_markdown(wiki, max_tokens=512, overlap=64):
            entries.append(chunk)

    # Estimate cost and abort if over cap BEFORE any API calls
    estimated_cost = estimate_cost(model_name, sum(len(e.text) for e in entries))
    if estimated_cost > budget_usd:
        abort(f"projected ${estimated_cost:.2f} exceeds cap ${budget_usd:.2f}; set BUILD_MAX_USD to override")

    # Embed
    vectors = []
    for entry in entries:
        if unchanged_since_last_run(entry.chunk_hash):
            vectors.append(cached_vector(entry.chunk_hash))
            continue
        vec, call_cost = embed(entry.text, model_name)
        cost_to_date += call_cost
        if cost_to_date > budget_usd:
            abort(f"cost accumulated to ${cost_to_date:.2f}; halting")
        vectors.append({"doc_key": entry.doc_key, "chunk_id": entry.chunk_id,
                        "chunk_hash": entry.chunk_hash, "vector": vec,
                        "layer": entry.layer, "path": entry.path})

    write_parquet(parquet_path, vectors)
    write_yaml(manifest_path, {
        "model": model_name, "model_version": get_model_version(model_name),
        "row_count": len(vectors), "skipped_count": len(skip_log),
        "refresh_ts": now_iso(), "cost_usd": cost_to_date,
    })

# scripts/knowledge/query_embeddings.py
def query(text, top_k=10, layer=None):
    manifest = load_yaml("data/document-index/embeddings-manifest.yaml")
    runtime_model = get_cli_model_arg_or_manifest(manifest)
    if runtime_model != manifest["model"]:
        exit_error(f"model mismatch: manifest={manifest['model']}, runtime={runtime_model}")
    q_vec = embed(text, runtime_model)
    results = cosine_topk(q_vec, load_parquet("data/document-index/embeddings.parquet"), top_k, layer_filter=layer)
    return [{"doc_key": r.doc_key, "chunk_id": r.chunk_id, "path": r.path,
             "similarity": r.score, "excerpt": r.text[:200]} for r in results]
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/build_embeddings_index.py` | main builder |
| Create | `scripts/knowledge/query_embeddings.py` | query CLI |
| Create | `scripts/knowledge/embeddings/__init__.py` | package |
| Create | `scripts/knowledge/embeddings/chunker.py` | markdown chunking |
| Create | `scripts/knowledge/embeddings/models.py` | pluggable model interface |
| Create | `scripts/knowledge/embeddings/cost.py` | per-model cost estimator + tracker |
| Create | `tests/knowledge/test_build_embeddings_index.py` | TDD |
| Create | `tests/knowledge/test_query_embeddings.py` | TDD |
| Create | `tests/knowledge/fixtures/embeddings/` | canned corpus |
| Create | `data/document-index/embeddings-manifest.yaml` | git-tracked manifest (initial empty) |
| Modify | `.gitignore` | exclude `data/document-index/embeddings.parquet` |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | nightly refresh |

---

## Acceptance Criteria

- [ ] All tests pass
- [ ] Stage-0 model pin from #2403 decision committed into `scripts/knowledge/embeddings/models.py`
- [ ] First real run writes manifest with row_count ≥1000 on current corpus
- [ ] Query p95 < 2s measured automatically in `test_query_p95_under_2s_on_fixture_corpus`
- [ ] Cost cap aborts before API calls exceed `BUILD_MAX_USD` (tested)
- [ ] Secrets never appear in manifest/logs (tested)
- [ ] `.gitignore` excludes `embeddings.parquet`; manifest remains git-tracked
- [ ] Nightly cron entry parses + schedules correctly
- [ ] sha256: enforced; md5: read-only; bare-hex rejected
- [ ] Review artifacts posted

---

## Risks and Open Questions

- **Risk:** Hard-dep on #2403 spike running to completion. Mitigation: #2403 is approved + its plan is ready; implementation can chain.
- **Risk:** Cost cap tuned for corpus-size-at-plan-time; corpus growth could drift. Mitigation: manifest records cost; cap is runtime-tunable via env.
- **Risk:** Wiki `doc_key` coverage low until #2360 lands — first build's `skipped_count` may be high. Mitigation: counts surfaced; non-blocking.
- **Open:** Cache-invalidation on corpus migration (e.g., if ledger `discovered → merged_at` rename per #2361 lands)? Plan default: manifest-version field; bump on schema change triggers full rebuild.

---

## Complexity: T2

Build + query + cron — bounded; no new architecture, builds on existing pipeline.
