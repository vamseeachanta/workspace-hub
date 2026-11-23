# WRK-1339 Stage 4 Plan — Naval Architecture Expert Agent via Deep Knowledge Extraction

## Context

We have 145 manifests from ~30 naval architecture textbooks/references and 110 ship plans. Today's session built multi-format parsers (EN400/Tupper/Attwood) and batch extraction scripts, but **the actual extraction has never run**. The 107 worked examples in JSONL are from a shallow classifier that mis-tags TOC entries. digitalmodel has 55 naval arch tests but most modules are stubs.

**End state:** A dual-persona expert skill — naval architect who is engineering + legal consultant — backed by source-traced, TDD-validated knowledge from 30 textbooks. No shortcuts: extract → validate → implement → synthesize.

**Key architectural decision:** Multi-provider extraction fork. Claude handles regex parsing, Codex handles poor-OCR PDFs (better PDF capabilities), Gemini provides cross-validation. Each provider plays to its strengths.

## Acceptance Criteria

- [ ] AC1: ≥150 deep-extracted worked examples with clean given/find/answer
- [ ] AC2: `use_as_test: true` flag on all records; ≥80 flagged testable
- [ ] AC3: Multi-provider extraction: Claude regex + Codex PDF fallback + Gemini cross-check
- [ ] AC4: Ship-specific hydrostatic tables for ≥4 vessels (DDG-51, FFG-7, CVN-65, AOE-6)
- [ ] AC5: ≥6 digitalmodel calculation modules with TDD from extracted examples
- [ ] AC6: Expert skill created with engineering + legal dual persona
- [ ] AC7: All responses cite textbook + page + equation number
- [ ] AC8: Regulatory compliance checker for ≥10 IMO/ABS/DNV criteria

## Scripts-Over-LLM Audit

| Operation | Recurs? | Action |
|---|---|---|
| Batch extraction | YES | `batch-deep-extract-naval.sh` (exists) |
| Quality assessment | YES | `assess-extraction-quality.py` (exists) |
| JSONL index rebuild | YES | `build-doc-intelligence.py --force` (exists) |
| Table curation | YES | `curate-promoted-tables.py` (WRK-1371, to create) |
| Cross-review submission | YES | `cross-review.sh <plan> all` (exists) |
| Codex PDF extraction | YES | `codex-extract-naval.sh` (WRK-1369, to create) |
| Provider routing | YES | `provider_recommender.sh` (exists) |

## Multi-Provider Extraction Architecture

### The Fork: Claude → Codex → Gemini

```
                    ┌─────────────────────┐
                    │  145 Naval Arch      │
                    │  Manifests           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Claude Regex        │
                    │  (3 format parsers)  │
                    │  batch-deep-extract  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Quality Gate        │
                    │  assess-extraction   │
                    │  -quality.py         │
                    └────┬────────────┬───┘
                         │            │
              examples≥3 │            │ examples<3
              per book   │            │ (poor OCR)
                         │            │
              ┌──────────▼──┐  ┌──────▼──────────┐
              │  PASS        │  │  Codex PDF       │
              │  Use Claude  │  │  Re-extraction   │
              │  results     │  │  codex-extract-  │
              │              │  │  naval.sh         │
              └──────────┬──┘  └──────┬───────────┘
                         │            │
                    ┌────▼────────────▼───┐
                    │  Gemini Cross-Check  │
                    │  Spot-check 20%     │
                    │  of numerical values │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Merged JSONL Index  │
                    │  extraction_source:  │
                    │  claude|codex|gemini │
                    └─────────────────────┘
```

### Provider Capability Routing

| Task | Claude | Codex | Gemini |
|------|--------|-------|--------|
| Regex parsing (Format A/B/C) | PRIMARY | — | — |
| Poor-OCR PDF re-extraction | — | PRIMARY | — |
| Numerical value cross-check | — | — | PRIMARY |
| GZ curve digitization | — | PRIMARY | VERIFY |
| Ship dimension extraction | — | PRIMARY | — |
| Regulatory requirement parsing | PRIMARY | VERIFY | — |

### Codex PDF Extraction Script (New)

```bash
# codex-extract-naval.sh — delegates to Codex for PDFs with poor OCR
# Reads extraction-yield-report.yaml, identifies books with <3 examples
# Submits PDF sections to Codex with structured output schema
# Merges results into deep extraction JSONL

codex exec "Extract all worked examples from this PDF section.
Return JSON: {number, title, given_inputs, expected_value, unit, page}" \
  --output-schema naval-example-schema.json \
  --output-last-message results.json
```

### Gemini Cross-Check Script (New)

```bash
# gemini-crosscheck-naval.sh — spot-checks 20% of extracted values
# Picks random sample from worked_examples.jsonl
# Submits to Gemini: "Verify: Example N.N from <book> page <P>.
#   Claude extracted expected_value=<V>. Is this correct?"
# Records agreement/disagreement in crosscheck-report.yaml

echo "$sample" | gemini -p "$prompt" -y --output-format json
```

## Revised Feature Decomposition

| # | WRK | Title | Scope | blocked_by | Agent |
|---|-----|-------|-------|------------|-------|
| 1 | 1369 | Run batch deep extraction | Execute parsers on 55 manifests | — | claude |
| 2 | 1370 | Curate TDD fixtures | Group examples into per-topic fixtures | 1369 | claude |
| 3 | 1371 | Table curation | Clean 3,683 CSVs to usable subset | — | claude |
| 4 | 1372 | Ship hydrostatic tables | DDG-51/FFG-7 curves of form data | 1369 | codex |
| 5 | 1373 | Seakeeping module | 6-DOF frequency-domain motion | 1372 | claude |
| 6 | 1374 | Advanced stability | Damage stability + IMO criteria | 1372 | claude |
| 7 | 1375 | Maneuverability module | Rudder forces + turning circle | — | claude |
| 8 | 1376 | Holtrop-Mennen resistance | Statistical resistance prediction | — | claude |
| 9 | 1377 | Hull form parametric design | Form coefficients + Series 60 | 1372 | claude |
| 10 | 1378 | Regulatory compliance engine | IMO/ABS/DNV automated checks | 1374 | claude |
| 11 | 1379 | Knowledge synthesis agent | Expert skill with knowledge query | 1370,1372,1376 | claude |
| 12 | 1380 | Ship dimensions manual entry | Fill template from 110 PDFs | — | codex |
| 13 | 1381 | GZ curve digitization | Digitize stability curves from figures | — | codex |
| 14 | 1382 | **Expert naval architect skill** | Dual persona: engineering + legal | 1379 | claude |

### Dependency Graph

```
Phase 1 — Extraction (parallel start)
  1369 (Claude batch extract) ─┬─► 1370 (Curate fixtures) ────────┐
                               └─► 1372 (Codex ship tables) ──┐   │
  1371 (Table curation) ─────────────────────────────────────┐ │   │
  1380 (Codex ship dimensions) ──────────────────────────────┤ │   │
  1381 (Codex GZ digitization) ──────────────────────────────┤ │   │
                                                             │ │   │
Phase 2 — Calculation Modules (after ship data)              │ │   │
  1376 (Holtrop-Mennen) ────────────────────────────────────┐│ │   │
  1375 (Maneuverability) ──────────────────────────────────┐││ │   │
  1372 ─► 1373 (Seakeeping) ─────────────────────────────┐│││ │   │
  1372 ─► 1374 (Stability) ─► 1378 (Regulatory) ───────┐││││ │   │
  1372 ─► 1377 (Hull form) ───────────────────────────┐ │││││ │   │
                                                      │ │││││ │   │
Phase 3 — Agent Synthesis                             │ │││││ │   │
  1370 + 1372 + 1376 ─► 1379 (Knowledge agent) ──────┤─┤┤┤┤┤─┤───┤
                                                      │ │││││ │   │
Phase 4 — Capstone                                    ▼ ▼▼▼▼▼ ▼   ▼
  1379 ─► 1382 (Expert Naval Architect Skill) ◄───── ALL FEED IN
```

## Pseudocode: Multi-Provider Extraction Pipeline

```python
def run_naval_extraction_pipeline(manifests, providers):
    # Step 1: Claude regex extraction on all manifests
    claude_results = batch_deep_extract(manifests, parser="multi_format")
    yield_report = assess_quality(claude_results)

    # Step 2: Identify poor-extraction books (< 3 examples)
    poor_books = [b for b in yield_report if b.example_count < 3]

    # Step 3: Codex PDF re-extraction on poor books
    for book in poor_books:
        codex_results = codex_extract_pdf_sections(book.pdf_path)
        merge_into(claude_results, codex_results, prefer="codex")

    # Step 4: Gemini spot-check 20% of all values
    sample = random_sample(claude_results + codex_results, frac=0.20)
    crosscheck = gemini_verify_values(sample)
    flag_disagreements(crosscheck)

    # Step 5: Final merge and index rebuild
    final = merge_all(claude_results, codex_results, crosscheck)
    rebuild_jsonl_indexes(final, prefer_deep=True)
    return final
```

## Test Plan

| # | What | Type | Expected |
|---|---|---|---|
| 1 | Multi-format parser dispatches correct strategy | Happy | EN400→en400_dnv, Tupper→tupper_biran, Attwood→attwood_pna |
| 2 | Codex fallback triggers on <3 examples | Edge | Books with poor OCR routed to Codex |
| 3 | Gemini cross-check flags incorrect value | Error | Disagreement recorded in crosscheck-report.yaml |
| 4 | Quality assessment sets use_as_test correctly | Happy | ≥1 input + expected_value → true |
| 5 | Deep records preferred over classifier in merge | Happy | extraction_source: deep overwrites classifier |
| 6 | Holtrop-Mennen resistance matches published values | Happy | Within 5% of textbook regression |
| 7 | IMO intact stability criteria pass for DDG-51 | Happy | All 6 criteria pass with margin |
| 8 | Expert skill cites source for every answer | Happy | Response contains textbook + page ref |

## Key Files

**Existing (implemented today):**
- `scripts/data/doc_intelligence/naval_example_parsers.py` — 3 strategy parsers
- `scripts/data/doc_intelligence/assess_extraction_quality.py` — quality flagging
- `scripts/data/doc-intelligence/batch-deep-extract-naval.sh` — batch runner
- `scripts/data/doc_intelligence/deep_extract.py` — wired to multi-format parser
- `data/doc-intelligence/en400-ch6-ch9-gap-findings.yaml` — gap confirmed

**To create (14 children):**
- `scripts/data/doc-intelligence/codex-extract-naval.sh` — Codex PDF fallback
- `scripts/data/doc-intelligence/gemini-crosscheck-naval.sh` — Gemini spot-check
- `scripts/data/doc-intelligence/curate-promoted-tables.py` — table cleanup
- `digitalmodel/src/digitalmodel/naval_architecture/holtrop_mennen.py` — resistance
- `digitalmodel/src/digitalmodel/naval_architecture/seakeeping.py` — 6-DOF
- `digitalmodel/src/digitalmodel/naval_architecture/damage_stability.py` — damage
- `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` — rudder
- `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` — parametric
- `digitalmodel/src/digitalmodel/naval_architecture/compliance.py` — regulatory
- `.claude/skills/digitalmodel/naval-architect-expert/SKILL.md` — capstone skill

## Verification

```bash
# All parser tests (38 pass)
uv run --no-project python -m pytest \
  scripts/data/doc_intelligence/tests/test_naval_example_parsers.py \
  scripts/data/doc_intelligence/tests/test_assess_extraction_quality.py \
  scripts/data/doc_intelligence/tests/test_generate_ship_dimension_template.py -v

# Batch extraction dry-run (55 manifests)
bash scripts/data/doc-intelligence/batch-deep-extract-naval.sh --dry-run

# Cross-review this plan
bash scripts/review/cross-review.sh specs/modules/delightful-fluttering-yao.md all --type plan --wrk-id WRK-1339
```

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Poor OCR yields <100 examples from Claude | Codex PDF fallback on books with <3 examples |
| Codex quota exhaustion | Opus fallback built into cross-review.sh |
| Gemini cross-check disagrees on >20% | Manual verification of disputed values |
| 110 ship plans have no extractable text | Codex primary for dimension extraction; manual fill as last resort |
| Regulatory requirements too vague for automation | Start with 10 binary checks (IMO intact stability); expand iteratively |
