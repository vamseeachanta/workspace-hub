# WRK-5040: promote-to-code.py — Promote All 8 Content Types

## Context

WRK-5038 built `build-doc-intelligence.py` which extracts document content into 8 JSONL indexes under `data/doc-intelligence/`. This script closes the loop: promoting those indexes into executable, testable code artifacts. Currently only `tables/index.jsonl` has data (6 records); all section-based indexes are empty but schema-defined. The architecture must handle both real data now and future extractions.

## Architecture

Mirrors `index_builder.py` pattern: thin CLI entry-point → core logic subpackage.

```
scripts/data/doc-intelligence/promote-to-code.py           # CLI (~80 lines)
scripts/data/doc_intelligence/promoters/
  __init__.py                                               # re-exports promote_all
  coordinator.py                                            # PromoteStats, promote_all(), _read_jsonl()
  text_utils.py                                             # sanitize_identifier, content_hash, write_atomic, source_citation
  constants.py                                              # → digitalmodel/.../naval_architecture/constants.py
  equations.py                                              # → digitalmodel/.../naval_architecture/equations.py
  tables.py                                                 # → data/standards/promoted/{domain}/
  worked_examples.py                                        # → tests/promoted/{domain}/test_*_examples.py
  curves.py                                                 # → CSV + scipy interpolation scaffold
  procedures.py                                             # → .claude/skills/engineering/{domain}/ YAML
  requirements.py                                           # → requirements Python module
  definitions.py                                            # → data/standards/promoted/{domain}/glossary.yaml
tests/data/doc_intelligence/
  test_promoter_coordinator.py                              # coordinator + integration
  test_promoter_constants.py                                # per-type unit tests
  test_promoter_equations.py
  test_promoter_tables.py
  test_promoter_definitions.py
  test_promoter_worked_examples.py
  test_promoter_procedures.py
  test_promoter_requirements.py
  test_promoter_curves.py
  fixtures/promote/                                         # fixture JSONL files
```

## Promoter Interface

Each promoter follows a uniform signature:

```python
def promote_<type>(records: list[dict], project_root: Path, dry_run: bool = False) -> PromoteResult
```

`PromoteResult` = `{files_written: list[str], files_skipped: list[str], errors: list[str]}`

## Output Mapping

| Type | Input | Output Location | Format |
|------|-------|-----------------|--------|
| constants | constants.jsonl | `digitalmodel/src/digitalmodel/naval_architecture/constants.py` | SCREAMING_SNAKE_CASE + docstrings (matches `dynacard/constants.py`) |
| equations | equations.jsonl | `digitalmodel/src/digitalmodel/naval_architecture/equations.py` | Typed functions + NumPy docstrings (matches `dnv_rp_b401.py`) |
| tables | tables/index.jsonl | `data/standards/promoted/{domain}/*.csv` | Copy CSV from `data/doc-intelligence/tables/` |
| worked_examples | worked_examples.jsonl | `tests/promoted/{domain}/test_{manifest}_examples.py` | pytest parametrized test cases |
| curves | curves/index.jsonl | CSV + `digitalmodel/.../naval_architecture/curves.py` | scipy.interpolate scaffold |
| procedures | procedures.jsonl | `.claude/skills/engineering/{domain}/` | YAML skill with frontmatter |
| requirements | requirements.jsonl | `data/standards/promoted/{domain}/requirements.py` | Module with string constants |
| definitions | definitions.jsonl | `data/standards/promoted/{domain}/glossary.yaml` | term/definition YAML |

## Idempotency

Every generated file includes `# content-hash: <sha256>` (Python) or `content_hash: <sha256>` (YAML). Re-run reads existing hash → skips if unchanged.

## Key Design Decisions

- **Subpackage over single file**: 8 promoters + utils would exceed 400-line limit
- **Regex parsing over LLM extraction**: Deterministic, testable (scripts-over-LLM-judgment rule)
- **Domain-based grouping**: Outputs grouped by `domain` field; supports future domains beyond `naval-architecture`
- **Content-hash idempotency**: Survives git operations; no false positives from timestamps

## Implementation Sequence (TDD)

| Step | Deliverable | Test File |
|------|-------------|-----------|
| 1 | Fixture JSONL files (8 types, 1-2 records each) | `fixtures/promote/` |
| 2 | `text_utils.py` — sanitize_identifier, content_hash, write_atomic, source_citation | `test_promoter_coordinator.py` |
| 3 | `coordinator.py` — PromoteResult, PromoteStats, _read_jsonl, promote_all | `test_promoter_coordinator.py` |
| 4 | `constants.py` — _parse_constants, _render_constants_module | `test_promoter_constants.py` |
| 5 | `tables.py` — CSV copy with domain grouping | `test_promoter_tables.py` |
| 6 | `equations.py` — _parse_equation, _render_equations_module | `test_promoter_equations.py` |
| 7 | `definitions.py` — _parse_definitions, _render_glossary | `test_promoter_definitions.py` |
| 8 | `worked_examples.py` — _parse_example, _render_test_module | `test_promoter_worked_examples.py` |
| 9 | `procedures.py` — _render_procedure_skill | `test_promoter_procedures.py` |
| 10 | `requirements.py` — requirements module renderer | `test_promoter_requirements.py` |
| 11 | `curves.py` — CSV + scipy scaffold | `test_promoter_curves.py` |
| 12 | `promote-to-code.py` CLI entry-point | CLI integration test |

## Critical Files (reuse patterns from)

- `scripts/data/doc_intelligence/index_builder.py` — coordinator pattern, _write_jsonl_atomic, BuildStats
- `scripts/data/doc-intelligence/build-doc-intelligence.py` — CLI pattern (sys.path, argparse)
- `digitalmodel/src/digitalmodel/marine_ops/artificial_lift/dynacard/constants.py` — constants output format
- `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` — equations output format
- `tests/data/doc_intelligence/test_index_builder.py` — test pattern

## Verification

```bash
# Run all promoter tests
uv run --no-project python -m pytest tests/data/doc_intelligence/test_promoter*.py -v

# Dry-run against real indexes
uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py --dry-run --verbose

# Full run (tables only — the only type with real data)
uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py --types tables --verbose

# Verify idempotency
uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py --types tables --verbose  # second run should show 0 written
```
