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

Create these scripts **first** before any document absorption begins.

## Phase 0: Foundation Setup (one-time)

### 0a. Scaffold specs directory
```
specs/wrk/WRK-1113/
  selection-matrix.md          ← candidate 10/10/10 list for Stage 5 user review
  doc-extracts/
    _template.yaml             ← template for worked-example extraction
  improvements-log.md          ← stub for analysis improvement notes
```

### 0b. Extend ledger schema
In `scripts/data/document-index/build-ledger.py` entry template (lines ~168-181):
```python
"exhausted": False,
"exhausted_at": None,
"absorbed_into": [],
```
Regenerate: `uv run --no-project python scripts/data/document-index/build-ledger.py`

### 0c. Add --exhausted filter to query-ledger.py
In `scripts/data/document-index/query-ledger.py` (after existing filters, lines ~102-111):
```python
parser.add_argument("--exhausted", action="store_true")
# ... filter:
if args.exhausted:
    standards = [s for s in standards if s.get("exhausted")]
```

### 0d. Create mark-exhausted.py
```python
# scripts/data/document-index/mark-exhausted.py <entry-id> <module-path>
# Loads ledger YAML, finds entry by id, sets exhausted=true/exhausted_at/absorbed_into, saves
```

### 0e. Create generate-coverage-report.py
```python
# scripts/data/document-index/generate-coverage-report.py
# Loads ledger, groups by domain, counts total/exhausted/done, writes docs/document-intelligence/domain-coverage.md
```

## Phase 1: 10/10/10 Selection Matrix (Stage 5 gate)

Draft `specs/wrk/WRK-1113/selection-matrix.md` listing all candidates from the WRK body
in a table format. User selects final 10 standards, 10 reports, 10 calculations at Stage 5.
**No implementation starts until selection is approved.**

## Phase 2: CP Document Absorption (per selected doc, ~10 CP docs)

Test file naming: `digitalmodel/tests/cathodic_protection/test_<standard>_doc_verified.py`
Module targets: `cathodic_protection/api_rp_1632.py`, `cathodic_protection/iso_15589_2.py`,
plus new `cathodic_protection/dnv_rp_b401.py` clean wrapper (typed functions, §X.Y refs).

**Per-document workflow (Steps 1–8):**

```
Step 1 — Write doc-extracts/<doc-ref>.yaml
  inputs: {area_m2: ..., current_density_a_m2: ..., coating_factor: ...}
  expected: {value: ..., unit: ..., note: "doc §X.Y states ..."}

Step 2 — Map to function in cathodic_protection/
  Found → Step 3 | Missing → Step 4 (gap-fill TDD)

Step 3 — Write verification test citing doc + section
  def test_<calc>_from_<doc_ref>_section_<N>(self):
      """Verify against worked example: <doc-ref> §N."""
      assert func(**inputs) == pytest.approx(expected, rel=0.01)

Step 4 — Gap-fill (only if Step 2 finds missing function)
  Write FAILING test first → implement minimal typed function → re-run → GREEN

Step 5 — Extract tabular data as module-level constants (no client refs)

Step 6 — Legal scan: bash scripts/legal/legal-sanity-scan.sh

Step 7 — Parametric sweep test (monotonicity or known trend)

Step 8 — Mark exhausted:
  uv run --no-project python scripts/data/document-index/mark-exhausted.py <id> <module>
```

## Phase 3: Drilling Riser Module (new)

**Namespace**: `digitalmodel/src/digitalmodel/drilling_riser/`

Files to create:
```
drilling_riser/
  __init__.py          ← exports all public functions
  stackup.py           ← riser tension capacity, wall thickness calc
  operability.py       ← RAO-based operability envelope (tabular lookup)
  tool_passage.py      ← tool passage / spacing calc
  damping.py           ← structural damping parametric
```

**Module pattern** (same as cathodic_protection/):
- Typed function signatures; module-level constants (SCREAMING_SNAKE_CASE with §X.Y refs)
- NumPy docstrings: summary line cites standard + section; Parameters/Returns sections
- No @doc_ref decorator — references inline in docstring and constants

**Test location**: `digitalmodel/tests/drilling_riser/test_<module>_doc_verified.py`
**Minimum**: ≥3 doc-verified functions + ≥3 doc-verified tests per function.

**TDD order**: doc-extracts YAML → failing test → minimal implementation → GREEN → sweep test.

## Phase 4: Exhaustion Marking

After all calcs for a document are absorbed:
```bash
uv run --no-project python scripts/data/document-index/mark-exhausted.py <entry-id> <module>
uv run --no-project python scripts/data/document-index/build-ledger.py
```

## Phase 5: Index Consolidation

Run coverage report:
```bash
uv run --no-project python scripts/data/document-index/generate-coverage-report.py
```
Commits `docs/document-intelligence/domain-coverage.md`.

Verify --exhausted filter:
```bash
uv run --no-project python scripts/data/document-index/query-ledger.py --exhausted
uv run --no-project python scripts/data/document-index/query-ledger.py --domain cathodic-protection --exhausted
```

## Acceptance Criteria Coverage

| AC | Phase | Artifact |
|----|-------|---------|
| selection-matrix.md drafted + user-approved | Phase 1 / Stage 5 | specs/wrk/WRK-1113/selection-matrix.md |
| doc-extracts/<doc-ref>.yaml per selected doc | Phase 2 | specs/wrk/WRK-1113/doc-extracts/ |
| ≥1 doc-verification test per calc | Phase 2 | tests/cathodic_protection/test_*_doc_verified.py |
| All existing CP tests still PASS | Phase 2 | CI run |
| Gap-fill functions follow module pattern | Phase 2 | cathodic_protection/*.py |
| All extracted tabular data passes legal scan | Phase 2 | legal-sanity-scan.sh exit 0 |
| improvements-log.md captures findings | Phase 2 | specs/wrk/WRK-1113/improvements-log.md |
| drilling_riser/ module ≥3 functions + tests | Phase 3 | digitalmodel/drilling_riser/ |
| Exhaustion marking applied | Phase 4 | standards-transfer-ledger.yaml |
| query-ledger --exhausted + --domain working | Phase 5 | query-ledger.py |
| domain-coverage.md committed | Phase 5 | docs/document-intelligence/ |
| Legal scan PASS all new code | All | legal-sanity-scan.sh |

## Critical Files

| File | Role |
|------|------|
| `digitalmodel/src/digitalmodel/cathodic_protection/api_rp_1632.py` | Pattern reference; test target |
| `digitalmodel/src/digitalmodel/cathodic_protection/iso_15589_2.py` | Pattern reference; test target |
| `digitalmodel/tests/cathodic_protection/test_api_rp_1632.py` | Test pattern reference |
| `scripts/data/document-index/query-ledger.py` | Extend with --exhausted filter |
| `scripts/data/document-index/build-ledger.py` | Extend entry template with exhausted fields |
| `data/document-index/standards-transfer-ledger.yaml` | Updated by mark-exhausted.py + build-ledger.py |
| `scripts/legal/legal-sanity-scan.sh` | Gate: all extracted data must pass |

## Verification

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
