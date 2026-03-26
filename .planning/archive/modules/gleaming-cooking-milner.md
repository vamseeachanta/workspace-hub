# WRK-5054: Run Doc-Intel Pipeline on Naval Architecture Collection

## Context

The doc-intelligence pipeline (WRK-5035–5041) is built and tested on a single introductory PDF. The 145 SNAME naval architecture PDFs are the first real corpus. This WRK validates the pipeline end-to-end and produces structured engineering data for digitalmodel.

## Plan

### Step 1: Batch Extract (textbooks → hydrostatics → ship plans)

Write a batch extraction script `scripts/data/doc-intelligence/batch-extract-naval.sh` that:
- Iterates over PDFs in priority order: textbooks (21), hydrostatics (13), ship plans (110)
- Calls `run-extract.sh --input <pdf> --domain naval-architecture --verbose` per file
- Logs per-file stats (sections, tables, figure refs) + errors to stdout
- Skips already-extracted files (manifest exists with matching checksum)
- Reports summary: total extracted, skipped, failed

**Key files:**
- `scripts/data/doc-intelligence/run-extract.sh` — existing wrapper
- `scripts/data/doc_intelligence/parsers/pdf.py` — pdfplumber extraction
- Output: `data/doc-intelligence/manifests/naval-architecture/*.manifest.yaml`

### Step 2: Build Indexes

```bash
uv run --no-project python scripts/data/doc-intelligence/build-doc-intelligence.py --force --verbose
```

- Rebuilds all 8 content-type JSONL indexes from manifests
- `--force` because existing checksums are from single ABS doc
- Expected output: constants.jsonl, equations.jsonl, requirements.jsonl, procedures.jsonl, definitions.jsonl, worked_examples.jsonl, tables/index.jsonl, curves/index.jsonl

### Step 3: Validate via Query

```bash
uv run --no-project python scripts/data/doc-intelligence/query-doc-intelligence.py --domain naval-architecture --type equations --keyword "resistance" --full
uv run --no-project python scripts/data/doc-intelligence/query-doc-intelligence.py --type constants --keyword "seawater" --full
uv run --no-project python scripts/data/doc-intelligence/query-doc-intelligence.py --type procedures --keyword "stability" --full
uv run --no-project python scripts/data/doc-intelligence/query-doc-intelligence.py --type definitions --keyword "metacentric" --full
```

If indexes are empty or thin: review classifier regex patterns in `scripts/data/doc_intelligence/classifiers.py` against actual extracted text. The classifiers were designed for technical documents but may need tuning for SNAME formatting conventions.

### Step 4: Promote to Code

```bash
uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py --verbose
```

Generates:
| Content type | Output path |
|---|---|
| constants | `digitalmodel/src/digitalmodel/naval_architecture/constants.py` |
| equations | `digitalmodel/src/digitalmodel/naval_architecture/equations.py` |
| requirements | `data/standards/promoted/naval-architecture/requirements.py` |
| procedures | `.claude/skills/engineering/naval-architecture/*.yaml` |
| definitions | `data/standards/promoted/naval-architecture/glossary.yaml` |
| tables | `data/standards/promoted/naval-architecture/*.csv` |
| curves | `digitalmodel/src/digitalmodel/naval_architecture/curves.py` (scaffold) |
| worked_examples | `tests/promoted/naval-architecture/test_*_examples.py` |

### Step 5: Create Naval Architecture Doc-Extraction Sub-Skill

Write `.claude/skills/engineering/doc-extraction/naval-architecture/SKILL.md` with:
- Domain heuristics for hull form coefficients, stability params, resistance equations
- IMO criteria references, classification rule tables
- Keyword patterns specific to naval architecture terminology

### Step 6: TDD Verification

Write tests that verify promoted Python functions against known textbook values:
- Holtrop resistance method (if extracted)
- ITTC 1957 friction line: `Cf = 0.075 / (log10(Re) - 2)^2`
- Seawater density ≈ 1025 kg/m³
- IMO weather criterion thresholds

Test location: alongside promoted worked examples in `tests/promoted/naval-architecture/`

## Critical Dependencies

- `/mnt/ace/docs/_standards/SNAME/` must be mounted and readable
- `pdfplumber` available via `uv run --with pdfplumber`
- Classifier patterns may need tuning post-extraction

## Verification

1. Count manifests: `ls data/doc-intelligence/manifests/naval-architecture/*.manifest.yaml | wc -l` → 145
2. Count non-empty JSONL: `wc -l data/doc-intelligence/*.jsonl` → >0 for at least 3 types
3. Query returns results for stability, resistance, hydrostatics
4. Promoted Python files exist and pass `uv run python -c "import ..."`
5. TDD tests pass: `uv run --no-project python -m pytest tests/promoted/naval-architecture/ -v`

## Risk: Thin Extraction

Ship plans (110 PDFs) are mostly drawings — pdfplumber will extract minimal text. This is expected. The real value comes from textbooks (21) and hydrostatics (13). If total classified content across all 145 PDFs is <50 records, the classifier patterns need tuning — that becomes a follow-up WRK, not scope creep here.
