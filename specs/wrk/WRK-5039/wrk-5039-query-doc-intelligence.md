# WRK-5039: query-doc-intelligence.py + Stage 2 Integration

## Mission
Query CLI for federated content indexes + Stage 2 resource-intelligence integration.

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/data/doc-intelligence/query-doc-intelligence.py` | CLI entry point |
| `scripts/data/doc_intelligence/query.py` | Core query logic |
| `tests/data/doc_intelligence/test_query.py` | TDD tests |

## Core API (query.py)

- `query_indexes(index_dir, content_type, domain, keyword, limit) -> list[dict]`
- `format_stage2_brief(results, content_type) -> str`
- `format_full(results) -> str`

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--type` | all | Content type filter |
| `--domain` | None | Domain filter |
| `--keyword` | None | Case-insensitive substring match |
| `--stage2-brief` | False | Concise output for Stage 2 injection |
| `--full` | False | Detailed output with source refs |
| `--limit` | 20 | Max results |
| `--json` | False | Raw JSON output |
| `--index-dir` | data/doc-intelligence | Index directory |

## Exit Codes
- 0: results found
- 1: no results
- 2: error

## Stage 2 Integration
Add `doc_intelligence_context:` key to resource-intelligence.yaml during Stage 2.
Called via: `query-doc-intelligence.py --stage2-brief --domain <domain>`

## TDD Tests (~18)
- Query by each content type
- Domain filter
- Keyword filter
- Combined filters
- Empty index → empty list
- stage2-brief format
- full format
- Exit codes (0, 1, 2)
- Limit flag
- Tables query (different schema)
- Curves query (different schema)
