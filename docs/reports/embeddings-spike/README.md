# Embeddings spike — per-model measurement reports

This directory receives per-model JSON outputs from
`scripts/knowledge/run_embeddings_spike.py` during the measurement phase of
issue #2403.

Each run produces one file per model using the pattern
`<model>-<UTC-ISO-timestamp>.json` (see `write_model_report` in the runner).

## Expected filenames after measurement

- `bge-m3-local-<ts>.json`
- `voyage-3-cloud-<ts>.json`
- `text-embedding-3-large-<ts>.json`

Each JSON document has the shape:

```json
{
  "model": "<model-name>",
  "corpus_docs_embedded": 500,
  "cost_usd": 0.00,
  "recall_at_10": 0.00,
  "p95_latency_ms": 0.0
}
```

## Status

Scaffold-phase — no measurement reports written yet. The scaffold landed on
`main` via `405ea2dc7`; measurement remains user-gated on
`OPENAI_API_KEY` / `VOYAGE_API_KEY` / local Ollama install for BGE-M3.

Once measurement completes, the decision doc at
`docs/document-intelligence/embeddings-model-selection.md` aggregates these
files into the rubric table and chosen-model rationale.
