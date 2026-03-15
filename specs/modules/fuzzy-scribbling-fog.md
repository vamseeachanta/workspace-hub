# WRK-1188: Phase B Extraction on og_standards — Implementation Plan

## Context

27,980 og_standards documents have zero LLM summaries or discipline classifications. This blocks semantic search, gap triage, and downstream calculations. The extraction pipeline (`phase-b-claude-worker.py`) and deep extraction tools (`deep_extract.py`, `extraction_learner.py`) are ready — this plan sequences their execution with an iterative learning loop.

**Key insight:** ASTM accounts for 25,572 of 27,980 docs. Their titles follow deterministic patterns ("Standard Specification for...") and designation prefixes map to disciplines. **Hybrid strategy:** run deterministic classifier on all ASTM ($0), then LLM-validate a random 100-doc sample to measure accuracy. If accuracy >90%, trust the rest; if not, expand LLM coverage. LLM is reserved for the 2,408 non-ASTM docs (~$5).

## Execution Plan

### Phase 0: Pre-flight Scripts (TDD first)

**Step 0a: ASTM deterministic classifier**
- New: `scripts/data/document-index/phase-b-astm-classifier.py`
- Reads SQLite `documents JOIN document_text` where `organization = 'ASTM'`
- Extracts real title from text header (first 500 chars)
- Maps ASTM designation prefix to discipline: A→materials, B→materials, C→materials, D→materials, E→materials, F→materials, G→cathodic-protection
- Writes summary JSON to `data/document-index/summaries/<content_hash>.json`
- Tests: `tests/data/document-index/test_astm_classifier.py`

**Step 0b: Checkpoint/reporting script**
- New: `scripts/data/document-index/phase-b-checkpoint.py`
- Reads summaries dir, filters by og_standards source
- Computes: discipline distribution, error rate, extraction method breakdown
- Writes YAML report to `data/document-index/checkpoints/`
- Tests: `tests/data/document-index/test_phase_b_checkpoint.py`

**Step 0c: Make claude-worker org-filterable**
- Modify: `scripts/data/document-index/phase-b-claude-worker.py`
- Add `--org <ORG>` CLI flag (process only that org)
- Add `--include-all` flag to remove ASTM/Unknown exclusion
- Keep current exclusion as default for backward compat

### Phase 1: High-Value Orgs — Learning Loop (~$2)

| Batch | Org(s) | Docs | Shards | Action |
|-------|--------|------|--------|--------|
| 1a | API (first 25) | 25 | 1 | Process → checkpoint → review → adjust prompt if needed |
| 1b | API (remainder) | ~510 | 4 | Full batch |
| 1c | DNV + ISO + Norsok | ~360 | 4 | Full batch |
| 1d | OnePetro + BSI + MIL + NEMA | ~165 | 2 | Full batch |

Checkpoint after each batch. Verify >90% non-"other" discipline rate.

### Phase 2: Unknown Org (~$1.30)

| Batch | Docs | Shards | Action |
|-------|------|--------|--------|
| 2a | Unknown (first 25) | 1 | Learning loop — review, may need prompt tuning |
| 2b | Unknown (remainder) | ~604 | 2 | Full batch |

### Phase 3: ASTM Hybrid — Deterministic + LLM Validation (~$0.20)

**Step 3a:** Run `phase-b-astm-classifier.py` on all 25,537 ASTM docs
- Pure Python + SQLite, no LLM — estimated 5-10 minutes
- Ambiguous docs (title extraction fails) → flagged for LLM

**Step 3b:** LLM-validate random 100 ASTM docs
- Sample 100 docs that the deterministic classifier already processed
- Run through `phase-b-claude-worker.py` to get LLM discipline
- Compare deterministic vs LLM classification — compute accuracy %
- **If accuracy >90%:** trust deterministic results, done
- **If accuracy <90%:** expand LLM to all ASTM docs where deterministic and LLM disagree (~$1-51 depending on disagreement rate)

**Step 3c:** Final checkpoint covering all 27,343 non-duplicate docs

### Phase 4: Deep Extraction on High-Value Docs

Run `deep-extract.py --input <pdf_path>` on ~20-30 API RP and DNV-RP documents:
- Extract tables → CSV, worked examples → pytest stubs, chart images → metadata
- Feed results into `extraction_learner.py` to capture domain patterns
- Use learnings to improve `doc-extraction/naval-architecture/SKILL.md` heuristics

Target docs (have worked examples):
- API RP 2A, API RP 2SK, API RP 1111, API 579
- DNV-RP-C203, DNV-RP-C205, DNV-RP-F109, DNV-RP-B401

### Phase 5: Pipeline Completion

1. Run Phase C: `uv run --no-project python scripts/data/document-index/phase-c-classify.py`
2. Run Phase E: `uv run --no-project python scripts/data/document-index/phase-e-backpopulate.py`
3. Generate final extraction report YAML
4. Regenerate index: `uv run --no-project python .claude/work-queue/scripts/generate-index.py`

## Budget

| Phase | Docs | LLM Cost |
|-------|------|----------|
| Phase 1 (API+DNV+ISO+etc) | 1,062 | ~$2.12 |
| Phase 2 (Unknown) | 629 | ~$1.26 |
| Phase 3a (ASTM deterministic) | 25,537 | $0.00 |
| Phase 3b (ASTM LLM validation sample) | 100 | ~$0.20 |
| Phase 3b (ASTM LLM expansion if needed) | 0-25,537 | $0-$51 |
| **Total (best case)** | **27,728** | **~$4.58** |
| **Total (worst case)** | **27,728** | **~$55** |

Well under $200 budget. Daily spend under $20.

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/data/document-index/phase-b-astm-classifier.py` | Deterministic ASTM classifier |
| `scripts/data/document-index/phase-b-checkpoint.py` | Batch checkpoint reporter |
| `tests/data/document-index/test_astm_classifier.py` | TDD tests for ASTM classifier |
| `tests/data/document-index/test_phase_b_checkpoint.py` | TDD tests for checkpoint |

## Files to Modify

| File | Change |
|------|--------|
| `scripts/data/document-index/phase-b-claude-worker.py` | Add `--org` and `--include-all` CLI flags |
| `scripts/data/document-index/launch-batch.sh` | Pass `--org` flag through to workers |

## Verification

1. After Phase 0: Run TDD tests for ASTM classifier and checkpoint script
2. After Phase 1: Checkpoint YAML shows >90% classified (non-"other") for API/DNV/ISO
3. After Phase 3: Checkpoint YAML shows all 27,343 docs have summaries with discipline
4. After Phase 5: `grep -c '"discipline"' data/document-index/summaries/*.json` matches doc count
5. After Phase 5: `phase-c-classify.py` completes without errors; enhancement-plan.yaml updated
6. Full doc_intelligence test suite: `PYTHONPATH=. uv run --no-project python -m pytest tests/data/doc_intelligence/ -v`
