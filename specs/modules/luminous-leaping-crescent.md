# WRK-1339 Plan — Deepen Naval Architecture Knowledge Extraction

## Context

Current extraction: 107 worked examples, 815 equations from ~30 naval architecture textbooks. Target: 300+ worked examples with clean given/find/answer separation, <5% OCR artifacts. Root cause of low yield: 15 textbooks have CID-corrupted text (pdfplumber can't resolve embedded fonts), and the worked example parser misses examples that span page boundaries.

## Acceptance Criteria

1. ≥300 worked examples with clean given/find/answer separation (scope narrowing: WRK spec says "all from all 30 docs" — count threshold is the measurable AC; completeness is Phase 3 goal)
2. Equations in proper LaTeX/structured notation (not garbled OCR)
3. Ship plans dimensional index: LOA, beam, draft, displacement for ≥50 vessels
4. `use_as_test: true/false` flag on every extraction record
5. <5% OCR artifacts in numerical values

## Yield Projections (cross-review P1-1 resolution)

| Phase | Source | Conservative | Optimistic |
|-------|--------|-------------|------------|
| Baseline | Current JSONL | 107 | 107 |
| Phase 1 (CID fix) | 15 corrupted textbooks recovered | +80 | +120 |
| Phase 2 (sliding window) | Cross-page examples caught | +30 | +50 |
| Phase 3 (EN400 Ch 5,6,9) | 3 missing chapters | +15 | +25 |
| Phase 3 (stability re-extract) | Biran deeper pass | +20 | +30 |
| Phase 3 (resistance re-extract) | PNA Vol II, Bertram | +15 | +25 |
| Phase 3 (other re-extracts) | Improved parsers on remaining books | +20 | +40 |
| **Total** | | **287** | **397** |

Conservative estimate falls slightly short — contingency: Tesseract OCR re-scan as second fallback for CID books where pypdfium2 also fails.

## Directory Convention Note (cross-review P2-3)

- `scripts/data/doc_intelligence/` — Python package (has `__init__.py`). Modify existing `.py` modules here.
- `scripts/data/doc-intelligence/` — CLI shell scripts and standalone Python scripts. Create new scripts here.

## OCR Artifact Taxonomy (cross-review P1-3)

An "OCR artifact in numerical values" is any of:
- `(cid:N)` character identifier codes in text
- Non-numeric characters in supposedly numeric fields (except `.`, `-`, `e`, `E`, `+`)
- Unit fields containing sentence fragments (>15 characters or containing spaces)
- Misrecognized digits where the value is clearly wrong (detected by range checks)

Denominator: total numerical fields across all JSONL records (inputs[].value + expected_value).

## Phase 1: Fix CID Corruption (highest leverage, +80-120 examples)

**Problem**: 15 of 32 text-bearing manifests contain `(cid:N)` garbage — pdfplumber can't resolve embedded fonts.

**Fix**: Add CID detection heuristic to `parsers/pdf.py` with `pdftotext` (poppler) fallback. pypdfium2 was tested but also fails on CID-corrupted fonts; pdftotext resolves them correctly.

**Actual findings**: 1 fully corrupted (Rawson-Tupper, 96.7%), 7 partially corrupted (1-7%), 24 clean, 113 empty (ship plans). Most textbooks already have clean text — CID fix primarily recovers Rawson-Tupper.

**Files to modify**:
- `scripts/data/doc_intelligence/parsers/pdf.py` — add `_has_cid_corruption()` + `_extract_with_pypdfium2()` fallback

**New scripts**:
- `scripts/data/doc-intelligence/diagnose-cid-manifests.py` — scan manifests, report CID corruption %
- `scripts/data/doc-intelligence/re-extract-cid-manifests.sh` — re-extract corrupted manifests with pypdfium2

**Child WRKs**: WRK-1370 (diagnose), WRK-1371 (add fallback), WRK-1372 (re-extract)

## Phase 2: Improve Parser Section-Boundary Handling (+30-50 examples)

**Problem**: "Example N.N" header on one page, "Solution:" on the next → parser misses it.

**Fix**: Sliding-window concatenation of adjacent sections (window=3) before feeding to parsers, with deduplication by `(source_book, number, page)`.

**Files to modify**:
- `scripts/data/doc_intelligence/deep_extract.py` — add `_windowed_sections()` pre-processor
- `scripts/data/doc_intelligence/naval_example_parsers.py` — fix unit extraction for garbled `output_unit` values

**Child WRKs**: WRK-1373 (sliding window), WRK-1374 (parser improvements)

## Phase 3: Re-extract All Textbooks

Re-run batch deep extraction on all 32 text-bearing manifests with improved pipeline.

**Existing scripts** (no changes): `batch-deep-extract-naval.sh`, `build-doc-intelligence.py`

**Files to modify**:
- `scripts/data/doc_intelligence/assess_extraction_quality.py` — fix `use_as_test` logic (handle both deep and classifier record formats)

**Child WRKs**: WRK-1375 (batch re-extract), WRK-1376 (fix use_as_test), WRK-1377 (EN400 Ch 5,6,9), WRK-1378 (stability domain), WRK-1379 (resistance domain)

## Phase 4: Ship Plans Dimensional Data

108 of 110 plans are drawing-only (no OCR text).

**Approach** (cross-review P1-2 resolution):
1. **Pilot**: Test LLM visual extraction on 5 diverse plans (battleship, submarine, destroyer, auxiliary, coast guard) before committing to full batch
2. **Primary source**: Cross-reference Jane's Fighting Ships and online ship databases for dimensional data (cheaper, more reliable)
3. **Supplementary**: LLM visual extraction on plan images where database lookup fails
4. **Fallback**: If combined yield <50, reduce AC3 target or defer remainder to future WRK

**New script**: `scripts/data/doc-intelligence/populate-ship-dimensions.py`

**Child WRK**: WRK-1380

## Phase 5: Quality Audit & JSONL Rebuild

**New scripts**:
- `scripts/data/doc-intelligence/audit-ocr-quality.py` — scan JSONL records for OCR artifacts in numerical fields
- `scripts/data/doc-intelligence/validate-extraction-yield.py` — verify ≥300 examples, use_as_test coverage, artifact rate

**Child WRKs**: WRK-1381 (OCR audit), WRK-1382 (final rebuild + yield validation)

## Dependency Graph

```
WRK-1370 → WRK-1371 → WRK-1372 → WRK-1375 → WRK-1381 → WRK-1382
             parallel:  WRK-1373 → WRK-1374 ─┘
             parallel:  WRK-1376 ─────────────────────────┘
             parallel:  WRK-1377 ─────┘
             parallel:  WRK-1380 (independent)
             after 1375: WRK-1378, WRK-1379
```

## Scripts to Create

| Script | Inputs | Outputs | Phase |
|--------|--------|---------|-------|
| `diagnose-cid-manifests.py` | manifests/*.yaml | stdout report | 1 |
| `re-extract-cid-manifests.sh` | CID manifest list | new manifests | 1 |
| `audit-ocr-quality.py` | *.jsonl indexes | artifact % report | 5 |
| `populate-ship-dimensions.py` | ship-plans-index.yaml, plan PDFs | ship-dimensions.yaml | 4 |
| `validate-extraction-yield.py` | all JSONL + ship-dimensions | pass/fail against ACs | 5 |

## Test Plan

| What | Type | Expected |
|------|------|----------|
| CID detection on known-corrupted manifest | Happy | Returns True, cid_ratio > 0.3 |
| pypdfium2 extraction on Rawson-Tupper PDF | Happy | Returns non-empty text for all pages |
| CID detection on clean manifest (Biran) | Edge | Returns False |
| Sliding window on split example (Example on p.17, Solution on p.18) | Happy | Parser finds example with correct inputs+answer |
| Deduplication after windowed parsing | Edge | No duplicate examples by (book, number, page) |
| `use_as_test` on record with inputs+expected_value | Happy | Returns True |
| `use_as_test` on record with no inputs | Edge | Returns False |
| OCR artifact scan on clean record | Happy | 0 issues |
| OCR artifact scan on `(cid:)` record | Error | Flagged as corrupted |
| End-to-end: total examples ≥ 300 | Happy | Pass |
| End-to-end: artifact rate < 5% | Happy | Pass |

## Verification

```bash
# After all phases complete:
uv run --no-project python scripts/data/doc-intelligence/validate-extraction-yield.py
# Expected: PASS on all 5 acceptance criteria

wc -l data/doc-intelligence/worked_examples.jsonl  # ≥ 300
uv run --no-project python scripts/data/doc-intelligence/audit-ocr-quality.py  # < 5%
jq -c 'select(.use_as_test == true)' data/doc-intelligence/worked_examples.jsonl | wc -l  # ≥ 150
```

## Cross-Review Notes

- 6 pending manual downloads (ABS, IMO, DTIC, UMich, Gillmer) not addressed — 300 target achievable without them; downloads deferred to separate WRK
- `naval_example_parsers.py` has 4 parser formats (EN400, Tupper/Biran, Attwood/PNA, LooseNumbered), not 3 as stated in earlier analysis
- No rollback strategy needed — baseline JSONL will be preserved (git-tracked) before re-extraction
