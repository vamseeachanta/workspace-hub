# Embeddings model-selection decision (#2403)

> **Status:** scaffold — measurement phase not yet run.
> **Blocker:** awaiting either `OPENAI_API_KEY` / `VOYAGE_API_KEY` provisioning OR a local `ollama` install (for BGE-M3).
> **Scaffold landed at:** commit pending this session.

## What exists now

- Eval set of 60 synthetic queries at `tests/fixtures/embeddings/eval-set.jsonl`, generated from `knowledge/wikis/marine-engineering/wiki/index.md` and `knowledge/wikis/engineering/wiki/index.md`. Each query has a `sha256:`-namespaced `target_doc_key` per operating-model §3.
- Spike runner at `scripts/knowledge/run_embeddings_spike.py` with:
  - Eval-set loader with per-row doc_key validation
  - Corpus validator (rejects non-`sha256:`/`md5:` keys)
  - `SpikeConfig.from_env()` for API-key + cost-cap loading
  - `CostCapExceeded` guard
  - Per-model JSON report writer to `docs/reports/embeddings-spike/<model>-<utc-ts>.json`
  - Decision-doc renderer with rubric table + chosen-model + commit-SHA fields
  - Stub runners for all 3 candidate models (raise `RuntimeError` until prereqs provisioned)
  - `--scaffold-check` CLI flag for validation without measurement
- Test suite at `tests/knowledge/test_embeddings_spike.py` — **12/12 passing**. Covers AC items, threat-model items, and decision-doc rendering. No live API calls.

## What remains (measurement phase — user-gated)

1. Provision at least one of:
   - `OPENAI_API_KEY` in env for `text-embedding-3-large`
   - `VOYAGE_API_KEY` in env for `voyage-3-cloud`
   - `ollama` installed locally with `ollama pull bge-m3` for BGE-M3 local
2. Fill in the real `embed()` impl in the three stub factories (`make_bge_m3_local_runner`, `make_voyage_runner`, `make_openai_runner`).
3. Wire the measurement loop: embed corpus sample of 500 wiki docs, compute query vectors, measure recall@10, p95 latency, and cost. Currently the loop is behind a `NotImplementedError` guard in `main()`.
4. Optionally upgrade the eval set from 60 synthetic queries to a mix with ≥25 hand-picked entries (mark `curation: "hand-picked"` in the JSONL per-row metadata). Synthetic queries satisfy the automated AC but a hand-picked mix produces more credible recall numbers.
5. Run `uv run python scripts/knowledge/run_embeddings_spike.py` end-to-end, commit per-model reports, populate this document with real numbers, pick a winner.

## Candidate models (per plan)

| Model | Locality | Price basis (approximate) | Prereq |
|---|---|---|---|
| BGE-M3 local | Local | $0 | `ollama pull bge-m3` |
| Voyage-3 cloud | Cloud | ~$0.12 / 1M tokens | `VOYAGE_API_KEY` |
| text-embedding-3-large | Cloud | ~$0.13 / 1M tokens | `OPENAI_API_KEY` |

Estimated total spend for 500-doc corpus + 60-query eval across both cloud models: ~$0.10 — well under the `SPIKE_MAX_USD=5` cap.

## Rubric (filled by measurement phase)

| Model | recall@10 | cost_usd | p95_latency_ms | corpus_docs_embedded |
|---|---|---|---|---|
| bge-m3-local | _pending_ | _pending_ | _pending_ | _pending_ |
| voyage-3-cloud | _pending_ | _pending_ | _pending_ | _pending_ |
| text-embedding-3-large | _pending_ | _pending_ | _pending_ | _pending_ |

## Rationale (filled by measurement phase)

_To be written once three rows above are populated. Planned decision criterion: highest recall@10 at acceptable cost (< cap) and acceptable p95 latency (< 500 ms for single-user query)._

## Measurement commit SHA

`_pending — will be populated by `render_decision_doc()` from `git rev-parse --short HEAD` at measurement time._`
