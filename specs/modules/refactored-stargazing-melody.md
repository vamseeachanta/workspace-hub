# WRK-1059 Plan Draft: Reference Documentation Quality Checks

## Context
`check-all.sh` (WRK-1056/1058) already runs ruff + mypy + `--docs` (basic README/docs/ checks).
Gap: no check that public API symbols have docstrings, no docs/ structure validation (index.md,
changelog), no build-system detection. API reference gaps create maintenance debt for contributors.

## What Was Designed (Route B — Medium)

### New file: `scripts/quality/api-audit.py`
AST-based scanner: enumerate all public classes/functions (no leading `_`) per repo's `src/`,
check each for a docstring, output JSON `{repo, total, with_docstring, coverage_pct}`.
- Under 200 lines. Uses only stdlib (`ast`, `json`, `pathlib`).
- Invoked via: `uv run --no-project python scripts/quality/api-audit.py <name> <src_path>`

### Extensions to `scripts/quality/check-all.sh`
1. `check_docs_structure(repo, path)` — warn if `docs/index.md` or `docs/index.rst` absent;
   warn if `CHANGELOG.md` / `docs/changelog.md` absent. Both warn-only (no exit 1).
2. `detect_build_system(repo, path)` — detect `docs/conf.py` (sphinx) / `mkdocs.yml` (mkdocs) /
   none. Informational; appended to `--docs` output line.
3. `--api` flag → calls `run_api_audit()` which calls `api-audit.py`; prints coverage % per repo.
   Warn-only (no exit 1 on low coverage — baseline capture only at this stage).
4. `--help` updated to show `--api`.

### Tests: `tests/quality/test_check_all.sh`
Six new test cases T15–T20:
- T15: `--docs` → `docs-index: WARN` when no index file
- T16: `--docs` → `docs-index: PASS` when `index.md` present
- T17: `--docs` → `changelog: WARN` when no changelog
- T18: `--docs` → `build: none` when no Sphinx/mkdocs files
- T19: `--api` → `api:` line in output
- T20: `--help` shows `--api`

## Acceptance Criteria Mapping
| AC | Delivered by |
|----|-------------|
| Public symbol audit across all 5 repos | `api-audit.py` + `run_api_audit()` in `check-all.sh --api` |
| Per-repo API docstring coverage % | JSON output + shell extraction |
| docs/ structure validated; missing files listed | `check_docs_structure()` |
| Codex cross-review passes | Stage 13 (post-execution) |

## Files Changed
- `scripts/quality/api-audit.py` (new, 77 lines)
- `scripts/quality/check-all.sh` (+~100 lines for 3 new functions + `--api` flag)
- `tests/quality/test_check_all.sh` (T15–T20 added, 35 total tests)

## Verification
```bash
# Run full test suite (35 tests)
bash tests/quality/test_check_all.sh

# Smoke test API audit on real repos
bash scripts/quality/check-all.sh --api

# Smoke test docs structure on real repos
bash scripts/quality/check-all.sh --docs
```
All 35 tests pass. `--api` outputs coverage lines for all 5 repos. `--docs` shows docs-index/changelog WARN for repos without them.
