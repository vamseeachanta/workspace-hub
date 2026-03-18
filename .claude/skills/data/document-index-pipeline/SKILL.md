---
name: document-index-pipeline
description: "Orchestrate the 7-phase document indexing pipeline (A\u2192G) for the 1M+ document corpus. Use when running\
  \ batch extraction, classification, or gap analysis on og_standards, ace_standards, or workspace_spec sources.\n"
version: 1.0.0
updated: 2026-03-15
category: data
triggers:
- document index
- phase b extraction
- phase c classify
- batch extraction
- og_standards
- run extraction pipeline
- document classification
---

# Document Index Pipeline

> 7-phase pipeline: Index → Extract → Classify → Data-Sources → Backpopulate → Gaps → Ledger

## Quick Reference

```
Phase A: index.jsonl (1M records)     — deterministic scan
Phase B: summaries/<sha>.json         — LLM discipline + deterministic ASTM
Phase C: enhancement-plan.yaml        — domain classification
Phase D: specs/data-sources/<repo>.yaml — legal-gated
Phase E: backpopulate index.jsonl     — deterministic heuristics
Phase F: WRK items from gaps          — deterministic
Phase G: standards-transfer-ledger    — deterministic merge
```

## Phase Commands

### Phase A — Index corpus
```bash
uv run --no-project python scripts/data/document-index/phase-a-index.py
```
- **Input**: Filesystem paths + og_standards SQLite (`/mnt/ace/O&G-Standards/_inventory.db`)
- **Output**: `data/document-index/index.jsonl` (1,033,933 records)
- **Resume-safe**: skips existing entries by path

### Phase 1.5 — Readability Enrichment (COMPLETE — WRK-1277)

Classification of all 1M+ PDFs is complete (96.7% coverage):
- native: 623,455 (60.3%) | machine: 278,899 (27.0%) | ocr-needed: 92,042 (8.9%)
- remaining errors: 6,221 (0.6%) — corrupt/missing/timeout edge cases

```bash
uv run --no-project python scripts/data/document-index/enrich-readability.py \
    --workers 10 --resume
```
- **Output**: updates index.jsonl records with `readability` field
- **Resume-safe**: `--resume` skips already-classified entries
- **Method**: pdftotext (poppler) via subprocess — NOT pdfplumber (see WARNING below)

> **WARNING (WRK-1277)**: pdfplumber in multiprocessing hangs in kernel D-state on
> NTFS/NFS mounts. Use pdftotext via `subprocess.run(timeout=30)` for batch work.
> See `pdf/pdftotext-poppler` sub-skill for proven code pattern.

### Phase 2 — Readability-Aware Deep Extraction

Deep extraction is split by readability classification:
- **Phase 2a**: machine-readable docs (pdftotext for text, pdfplumber for tables on single docs) — ~279K docs
- **Phase 2b**: OCR docs (~92K docs) — requires OCR preprocessing before extraction
- Yield assessment script: `assess-deep-extraction-yield.py` evaluates extraction quality across strata

### Phase B — Extract + classify (LLM)

**Non-ASTM orgs** (API, DNV, ISO, etc.) — LLM via Claude CLI:
```bash
# From INSIDE Claude Code (unset CLAUDECODE to avoid nesting):
env -u CLAUDECODE uv run --no-project python \
    scripts/data/document-index/phase-b-claude-worker.py \
    --shard 0 --total 1 --source og_standards --org API

# From SEPARATE terminal — parallel shards:
bash scripts/data/document-index/launch-batch.sh 10 og_standards
# With org filter:
bash scripts/data/document-index/launch-batch.sh 2 og_standards API
```

**ASTM docs** — deterministic (no LLM, $0):
```bash
uv run --no-project python scripts/data/document-index/phase_b_astm_classifier.py
# Dry run first:
uv run --no-project python scripts/data/document-index/phase_b_astm_classifier.py --dry-run --limit 50
```

**Validate ASTM accuracy** (requires prior LLM run on sample):
```bash
# Step 1: LLM-classify 100 ASTM docs in validate mode
env -u CLAUDECODE uv run --no-project python \
    scripts/data/document-index/phase-b-claude-worker.py \
    --shard 0 --total 1 --source og_standards --org ASTM \
    --include-all --validate --limit 100
# Step 2: Compare deterministic vs LLM
uv run --no-project python scripts/data/document-index/phase-b-astm-validate.py
```

**Checkpoint** (run after each batch):
```bash
uv run --no-project python scripts/data/document-index/phase_b_checkpoint.py \
    --source og_standards --label "batch-name"
```

### Phase C — Domain classification
```bash
uv run --no-project python scripts/data/document-index/phase-c-classify.py
```
- **Output**: `data/document-index/enhancement-plan.yaml`

### Phase D — Data source specs (legal-gated)
```bash
uv run --no-project python scripts/data/document-index/phase-d-data-sources.py
```

### Phase E — Backpopulate index
```bash
uv run --no-project python scripts/data/document-index/phase-e-backpopulate.py
```

### Phase F — Generate gap WRKs
```bash
uv run --no-project python scripts/data/document-index/phase-f-gap-wrk-generator.py
```

### Phase G — Build ledger
```bash
uv run --no-project python scripts/data/document-index/build-ledger.py
```

## Key Patterns

### Claude CLI inside Claude Code
The `claude` CLI cannot run nested inside Claude Code. Two options:
1. **`env -u CLAUDECODE`** — unset the guard variable (works for background tasks)
2. **Separate terminal** — run `launch-batch.sh` from a non-Claude-Code shell

### Resume safety
All Phase B scripts are resume-safe: `needs_llm(sha)` checks if `discipline` already
exists in `summaries/<sha>.json`. Re-running skips already-classified docs.

### Org filtering (Phase B)
```
--org API          # process only API standards
--org Unknown      # process only Unknown org
--include-all      # include ASTM/Unknown (normally excluded)
--validate         # write to llm_discipline (don't overwrite discipline)
```

### Budget tracking
- Haiku: ~$0.002/doc
- Daily cap: $20
- Total budget: $200
- ASTM deterministic: $0 (prefix mapping)

## Verification

```bash
# Count classified og_standards docs
uv run --no-project python -c "
import sqlite3, json; from pathlib import Path
conn = sqlite3.connect('/mnt/ace/O&G-Standards/_inventory.db')
rows = conn.execute('SELECT content_hash FROM documents WHERE is_duplicate=0').fetchall()
s = Path('data/document-index/summaries')
done = sum(1 for (h,) in rows if h and (s/f'{h}.json').exists() and json.loads((s/f'{h}.json').read_text()).get('discipline'))
print(f'{done}/{len(rows)} classified')
"
```

## Script Inventory

| Script | Deterministic | Lines | Purpose |
|--------|:---:|------:|---------|
| phase-a-index.py | Yes | 373 | Corpus scan → index.jsonl |
| phase-b-extract.py | Yes | 313 | Text extraction (no LLM) |
| phase_b_astm_classifier.py | Yes | 266 | ASTM prefix → discipline |
| phase_b_checkpoint.py | Yes | 154 | Batch stats report |
| phase-b-claude-worker.py | **LLM** | 423 | Claude CLI batch worker |
| phase-b-astm-validate.py | Yes | 153 | Compare det vs LLM |
| launch-batch.sh | Orch | 70 | Parallel shard launcher |
| phase-c-classify.py | Heuristic | 345 | Domain classification |
| phase-d-data-sources.py | Yes | 283 | Per-repo data source specs |
| phase-e-backpopulate.py | Yes | 222 | Backfill index.jsonl fields |
| phase-e2-remap.py | Yes | 506 | Targeted reclassification |
| enrich-readability.py | Yes | — | PDF readability classification (machine/ocr/mixed/error) |
| assess-deep-extraction-yield.py | Yes | — | Evaluate deep extraction quality across strata |
| phase-f-gap-wrk-generator.py | Yes | 398 | Gap → WRK items |
| build-ledger.py | Yes | 380 | Standards transfer ledger |
| query-ledger.py | Yes | 125 | Ledger query tool |

**Deterministic: 14/16 scripts (88%). LLM-dependent: 2/16 (12%).**
