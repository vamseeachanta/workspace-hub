# WRK-5042: Batch Extraction Pipeline

## Context

WRK-5037 delivered `extract-document.py` (single-doc extraction) and WRK-5038 delivered federated content indexes. Scaling to a 1M-document corpus requires queue management, rate limiting, cost visibility, failure recovery, and resume capability. This pipeline bridges single-doc extraction to corpus-scale processing.

## Architecture

One new Python script + one YAML queue schema + TDD tests. Reuses existing infrastructure heavily.

### New Files

| File | Purpose |
|------|---------|
| `scripts/data/doc-intelligence/batch-extract.py` | CLI batch runner (~200 lines) |
| `scripts/data/doc_intelligence/queue.py` | Queue state management module (~150 lines) |
| `scripts/data/doc_intelligence/tests/test_batch_extract.py` | TDD tests |
| `config/doc-intelligence/extraction-queue-example.yaml` | Example queue config |

### Reused Infrastructure

| File | Usage |
|------|-------|
| `scripts/data/doc-intelligence/extract-document.py` | Called per document (subprocess or direct import) |
| `scripts/data/doc_intelligence/schema.py` | `DocumentManifest`, `write_manifest()` atomic write pattern |
| `scripts/ai/wrk_cost_report.py` | Cost record schema for JSONL emission |
| `scripts/data/doc_intelligence/orchestrator.py` | `get_parser()` for pre-flight format validation |

## Queue YAML Schema (`extraction-queue.yaml`)

```yaml
version: "1.0"
queue:
  name: "naval-architecture-corpus"
  created_at: "2026-03-13T00:00:00Z"

documents:
  - path: "/mnt/ace/docs/_standards/SNAME/doc1.pdf"
    domain: "naval-architecture"
    doc_ref: "SNAME-001"
    status: pending        # pending | processing | completed | failed
    error: null
    manifest_path: null
    processed_at: null

settings:
  batch_size: 50           # docs per batch before checkpoint
  rate_limit: 2.0          # seconds between extractions
  output_dir: "data/doc-intelligence/manifests"
  dry_run: false
```

## `queue.py` — Queue State Module

```python
# Key functions:
load_queue(path: Path) -> dict           # Parse queue YAML
save_queue(queue: dict, path: Path)      # Atomic write (tmpfile + os.replace)
get_pending(queue: dict) -> list[dict]   # Filter status == "pending"
get_stats(queue: dict) -> dict           # {pending: N, completed: M, failed: K, total: T}
mark_completed(doc: dict, manifest_path: str)
mark_failed(doc: dict, error: str)
```

## `batch-extract.py` — CLI

```
uv run --no-project python scripts/data/doc-intelligence/batch-extract.py \
  --queue config/doc-intelligence/extraction-queue.yaml \
  [--batch-size 50] [--rate-limit 2.0] [--resume] [--dry-run] [--verbose]
```

### Processing Loop

```
1. Load queue YAML
2. Filter pending docs (if --resume, skip completed/failed)
3. For each doc in batch:
   a. Mark status = "processing"
   b. Call extract-document.py (subprocess: captures exit code)
   c. On success: mark_completed() with manifest_path
   d. On failure: mark_failed() with error message
   e. Sleep rate_limit seconds
   f. Every batch_size docs: save_queue() checkpoint
4. Save final queue state
5. Print health summary (processed/pending/failed)
6. Emit cost summary line to stdout
```

### Cost Tracking

Append one JSONL record to `.claude/state/session-signals/cost-tracking.jsonl` per batch run:
```json
{"ts": "...", "provider": "script", "model": "batch-extract",
 "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
 "wrk": "WRK-5042", "estimated": false,
 "batch_stats": {"processed": 50, "failed": 2, "duration_s": 120}}
```

Note: extraction itself has no LLM cost — cost_usd=0. The record tracks batch execution metadata for audit trail. Real LLM cost tracking applies if extraction later integrates LLM classification.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All docs processed successfully |
| 1 | Some docs failed (partial success) |
| 2 | Queue file not found or invalid |
| 3 | No pending documents |

## TDD Test Plan

| # | Test | What it validates |
|---|------|-------------------|
| 1 | `test_load_queue_valid` | Parses well-formed queue YAML |
| 2 | `test_load_queue_missing_file` | Raises FileNotFoundError |
| 3 | `test_load_queue_invalid_yaml` | Raises ValueError |
| 4 | `test_get_pending_filters_completed` | Only returns status=pending |
| 5 | `test_get_stats_counts` | Correct pending/completed/failed/total |
| 6 | `test_mark_completed_updates_fields` | Sets status, manifest_path, processed_at |
| 7 | `test_mark_failed_records_error` | Sets status=failed, error message |
| 8 | `test_save_queue_atomic_write` | Uses tmpfile + os.replace |
| 9 | `test_batch_extract_dry_run` | No docs processed, summary printed |
| 10 | `test_batch_extract_rate_limit` | Enforces delay between docs |
| 11 | `test_batch_extract_checkpoint` | Saves queue every batch_size docs |
| 12 | `test_batch_extract_resume` | Skips completed docs on resume |
| 13 | `test_batch_extract_failure_tracking` | Failed docs get error recorded |
| 14 | `test_batch_extract_exit_codes` | Correct exit code per scenario |
| 15 | `test_batch_extract_all_completed` | Exit 3 when no pending docs |

## Implementation Sequence

1. Write TDD tests for `queue.py` (tests 1-8)
2. Implement `queue.py` — pass all queue tests
3. Write TDD tests for `batch-extract.py` (tests 9-15)
4. Implement `batch-extract.py` — pass all batch tests
5. Create `extraction-queue-example.yaml`
6. Integration test: run against 3-5 real docs from `data/doc-intelligence/manifests/`

## Verification

```bash
# Run all tests
uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/test_batch_extract.py -v

# Dry run against example queue
uv run --no-project python scripts/data/doc-intelligence/batch-extract.py \
  --queue config/doc-intelligence/extraction-queue-example.yaml --dry-run

# Real run with small batch
uv run --no-project python scripts/data/doc-intelligence/batch-extract.py \
  --queue config/doc-intelligence/extraction-queue-example.yaml \
  --batch-size 3 --rate-limit 1.0

# Resume after interruption
uv run --no-project python scripts/data/doc-intelligence/batch-extract.py \
  --queue config/doc-intelligence/extraction-queue-example.yaml --resume
```

## Scope Boundaries

**In scope:** Queue YAML management, batch runner, rate limiting, resume, failure tracking, health summary, cost audit record.

**Out of scope:** Parallel extraction (future WRK), LLM-based classification during extraction, auto-index rebuild after batch, web dashboard (health is CLI-only).
