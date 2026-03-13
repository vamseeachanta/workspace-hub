# WRK-5038: build-doc-intelligence.py + Federated Content Indexes

## Context

WRK-5037 delivered a document extraction pipeline that produces YAML manifests with raw
sections, tables, and figure_refs. WRK-5038 builds the next layer: a federated index
builder that reads all manifests and produces 8 content-type JSONL indexes for fast
querying without re-parsing source documents.

## Architecture

```
data/doc-intelligence/manifests/<domain>/*.manifest.yaml  (INPUT — from WRK-5037)
                          │
              build-doc-intelligence.py
                          │
    ┌─────────┬───────────┼───────────┬──────────┐
    ▼         ▼           ▼           ▼          ▼
constants  equations  procedures  tables/    manifest-
.jsonl     .jsonl     .jsonl      ├─*.csv    index.jsonl
                                  └─index.jsonl
definitions  requirements  worked_examples  curves/
.jsonl       .jsonl        .jsonl           ├─*.csv
                                            └─index.jsonl
```

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/data/doc-intelligence/build-doc-intelligence.py` | CLI entry point |
| `scripts/data/doc_intelligence/index_builder.py` | Core builder logic |
| `scripts/data/doc_intelligence/classifiers.py` | Heuristic content-type classifiers |
| `tests/data/doc_intelligence/test_index_builder.py` | TDD tests |
| `tests/data/doc_intelligence/test_classifiers.py` | Classifier tests |

## Files to Reuse (no modification)

| File | What we reuse |
|------|---------------|
| `scripts/data/doc_intelligence/schema.py` | `manifest_from_dict()`, `DocumentManifest`, all dataclasses |
| `scripts/data/doc_intelligence/utils.py` | `doc_ref` generation |

## Implementation Plan

### Step 1: TDD — test fixtures + classifier tests

Create `tests/data/doc_intelligence/fixtures/` with 2-3 small synthetic manifests:
- One with sections containing constants ("GM = 1.5 m"), equations ("R_T = ..."),
  definitions ("means", "is defined as"), requirements ("shall"), procedures (numbered steps),
  worked examples ("Example:", given/find/solution)
- One with tables and figure_refs
- One empty manifest (edge case)

Write failing tests for `classifiers.py`:
- `classify_section(section) -> str|None` returns content type or None
- Heuristic rules: keyword matching on section text
  - constants: `=` + units pattern, "constant", symbol definitions
  - equations: math operators, Greek letters, numbered equations
  - procedures: numbered steps, "step 1", sequential action verbs
  - requirements: "shall", "must", "required", normative language
  - definitions: "means", "is defined as", "refers to", glossary context
  - worked_examples: "example", "sample calculation", given/find patterns

### Step 2: TDD — index builder tests

Write failing tests for `index_builder.py`:
- `build_indexes(manifest_dir, output_dir) -> BuildStats`
- Test: reads fixture manifests → produces correct JSONL files
- Test: incremental rebuild skips unchanged (checksum match in manifest-index)
- Test: tables produce CSV + tables-index.jsonl
- Test: curves produce CSV + curves-index.jsonl
- Test: manifest-index.jsonl contains all processed manifests
- Test: summary stats are correct

### Step 3: Implement classifiers.py

Heuristic classifier for each content type. Each section is tested against all
classifiers; first match wins (priority order: requirements > constants > equations >
procedures > definitions > worked_examples). Unclassified sections are skipped.

### Step 4: Implement index_builder.py

Core logic:
1. Scan `manifest_dir` recursively for `*.manifest.yaml`
2. Load existing `manifest-index.jsonl` if present → build checksum map
3. For each manifest not in checksum map (or checksum changed):
   a. Load via `manifest_from_dict(yaml.safe_load(...))`
   b. Classify each section → append to content-type accumulators
   c. Pass-through tables → write CSV to `tables/<manifest>-table-N.csv`
   d. Pass-through figure_refs → write to `curves/` (if curve-like)
   e. Record in manifest-index
4. Write all JSONL indexes atomically (tmpfile + os.replace)
5. Print summary stats

### Step 5: Implement CLI entry point

`build-doc-intelligence.py`:
```
--manifest-dir  (default: data/doc-intelligence/manifests)
--output-dir    (default: data/doc-intelligence)
--force         (rebuild all, ignore checksums)
--verbose       (print per-manifest details)
--dry-run       (scan only, don't write)
```

### Step 6: Run all tests green

## JSONL Record Schemas

### manifest-index.jsonl
```json
{"manifest_path": "...", "domain": "...", "filename": "...", "checksum": "...",
 "counts": {"sections": 6, "tables": 2, "constants": 1, "equations": 0, ...},
 "indexed_at": "ISO8601"}
```

### constants.jsonl
```json
{"name": "...", "symbol": "...", "value": "...", "units": "...",
 "source": {"document": "...", "page": 3, "section": "..."}, "domain": "...",
 "manifest": "..."}
```

### equations.jsonl
```json
{"name": "...", "expression": "...", "variables": ["..."],
 "source": {...}, "domain": "...", "manifest": "..."}
```

### tables-index.jsonl
```json
{"title": "...", "columns": ["..."], "row_count": 4, "csv_path": "tables/...",
 "source": {...}, "domain": "...", "manifest": "..."}
```

### curves-index.jsonl
```json
{"title": "...", "figure_id": "...", "caption": "...", "csv_path": "curves/...",
 "source": {...}, "domain": "...", "manifest": "..."}
```

### procedures.jsonl / requirements.jsonl / definitions.jsonl / worked_examples.jsonl
Each follows: `{"text": "...", "source": {...}, "domain": "...", "manifest": "..."}`
with type-specific fields extracted when detectable.

## Key Design Decisions

1. **Heuristic classifiers, not LLM** — deterministic, fast, testable; can be upgraded later
2. **First-match priority** — avoids double-counting sections
3. **Tables pass-through** — manifest tables go directly to tables index (already structured)
4. **Figure refs → curves** — figure_refs are the closest proxy; actual data_points require OCR (future work)
5. **Atomic writes** — same pattern as schema.py (tmpfile + os.replace)
6. **Incremental via checksum** — manifest checksum from metadata.checksum field

## Verification

```bash
# Run tests
uv run --no-project python -m pytest tests/data/doc_intelligence/test_classifiers.py -v
uv run --no-project python -m pytest tests/data/doc_intelligence/test_index_builder.py -v

# Run builder against real manifest
uv run --no-project python scripts/data/doc-intelligence/build-doc-intelligence.py --verbose

# Verify outputs exist
ls data/doc-intelligence/*.jsonl
ls data/doc-intelligence/tables/
ls data/doc-intelligence/curves/

# Verify incremental (second run should skip)
uv run --no-project python scripts/data/doc-intelligence/build-doc-intelligence.py --verbose
# Should show "0 manifests updated"
```
