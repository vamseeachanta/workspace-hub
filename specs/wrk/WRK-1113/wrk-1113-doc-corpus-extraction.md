# WRK-1113 Plan: Document Corpus Parametric Extraction
> Phase 1: Drilling Riser + Cathodic Protection

## Context

The workspace document corpus exists to serve one purpose: eliminate re-reading source
documents by integrating their data and calculations directly into the codebase. This WRK
formalises the extraction pipeline for Phase 1 (Drilling Riser + CP), producing:
- Doc-verified tests that assert route implementations match standard worked examples
- Gap-fill functions where calculations are missing
- A drilling riser parametric module (new namespace)
- Exhaustion marking in the standards-transfer-ledger once content is absorbed

## Design Decisions

- **Drilling riser namespace**: `digitalmodel/src/digitalmodel/drilling_riser/` (new top-level module, parallel to `cathodic_protection/`). Drilling riser calcs are mechanical engineering — separating them from CP is correct semantically.
- **CP test targets**: `cathodic_protection/` primary layer only (`api_rp_1632.py`, `iso_15589_2.py`, plus new wrappers). `infrastructure/` routes are read-only reference; not test targets for this WRK.

## Scripts to Create (scripts-over-LLM audit)

Both operations recur ≥25% (once per absorbed document across 30 docs in Phase 1 alone):

| Script | Purpose | Recurs? |
|--------|---------|---------|
| `scripts/data/document-index/mark-exhausted.py <id> <module>` | Sets `exhausted: true`, `exhausted_at`, `absorbed_into` in ledger YAML | YES — once per doc |
| `scripts/data/document-index/generate-coverage-report.py` | Writes `docs/document-intelligence/domain-coverage.md` from ledger query | YES — every doc-intel WRK |

## Phase 0: Foundation Setup

### 0a. Scaffold specs directory
```
specs/wrk/WRK-1113/
  selection-matrix.md          ← candidate 10/10/10 list for Stage 5 user review
  doc-extracts/
    _template.yaml             ← template for worked-example extraction
  improvements-log.md          ← stub for analysis improvement notes
```

### 0b. Extend ledger schema
Add to build-ledger.py entry template:
```python
"exhausted": False,
"exhausted_at": None,
"absorbed_into": [],
```

### 0c. Add --exhausted filter to query-ledger.py
```python
parser.add_argument("--exhausted", action="store_true")
if args.exhausted:
    standards = [s for s in standards if s.get("exhausted")]
```

### 0d. Create mark-exhausted.py
```
scripts/data/document-index/mark-exhausted.py <entry-id> <module-path>
```
Loads ledger YAML, finds entry by id, sets exhausted=true/exhausted_at/absorbed_into, saves.

### 0e. Create generate-coverage-report.py
```
scripts/data/document-index/generate-coverage-report.py
```
Loads ledger, groups by domain, counts total/exhausted/done, writes docs/document-intelligence/domain-coverage.md.

## Phase 1: 10/10/10 Selection Matrix (User Gate)

Draft `specs/wrk/WRK-1113/selection-matrix.md` listing all candidates.
**No Phase 2+ implementation starts until user selects 10/10/10 and approves.**

## Phase 2: CP Document Absorption (per selected doc)

Test file naming: `digitalmodel/tests/cathodic_protection/test_<standard>_doc_verified.py`

Per-document workflow:
1. Write doc-extracts/<doc-ref>.yaml (inputs + expected from worked example)
2. Map to function in cathodic_protection/
3. Write verification test citing doc + section
4. Gap-fill if function missing (TDD: failing test → minimal impl → GREEN)
5. Extract tabular data as module-level constants (legal-gated)
6. Legal scan
7. Parametric sweep test
8. Mark exhausted

## Phase 3: Drilling Riser Module (new)

Namespace: `digitalmodel/src/digitalmodel/drilling_riser/`

Files:
- `__init__.py` — exports all public functions
- `stackup.py` — riser tension capacity, wall thickness calc
- `operability.py` — RAO-based operability envelope (tabular lookup)
- `tool_passage.py` — tool passage / spacing calc
- `damping.py` — structural damping parametric

Test location: `digitalmodel/tests/drilling_riser/test_<module>_doc_verified.py`
Minimum: ≥3 doc-verified functions + ≥3 doc-verified tests per function.

## Phase 4: Exhaustion Marking

Run mark-exhausted.py + rebuild ledger for each absorbed doc.

## Phase 5: Index Consolidation

Run generate-coverage-report.py → commits domain-coverage.md.
Verify --exhausted and --domain filters working.

## Acceptance Criteria

See WRK-1113 body in .claude/work-queue/working/WRK-1113.md

## Verification Commands

```bash
# CP tests (existing + new doc-verified)
cd digitalmodel && uv run python -m pytest tests/cathodic_protection/ -v

# Drilling riser tests
cd digitalmodel && uv run python -m pytest tests/drilling_riser/ -v

# Ledger exhausted filter
uv run --no-project python scripts/data/document-index/query-ledger.py --exhausted

# Legal scan
bash scripts/legal/legal-sanity-scan.sh

# Coverage report
uv run --no-project python scripts/data/document-index/generate-coverage-report.py
```
