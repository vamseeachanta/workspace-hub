# WRK-1085 Plan — Claude

## Summary
Fast cross-repo symbol index and search tooling. Three deliverables: AST-based symbol
indexer, sub-second find-symbol lookup, ranked cross-repo grep wrapper.

## Phase 1: Symbol Indexer (3pts)
- `scripts/search/build-symbol-index.py`
  - Walk all 5 tier-1 `src/` roots via `os.walk`
  - Parse each `.py` file with `ast.parse`; skip + warn on SyntaxError
  - Emit `class`, `function`, `method`, `constant` (SCREAMING_SNAKE_CASE) records
  - Write `config/search/symbol-index.jsonl` (one JSON line per symbol)
  - Print summary: `N records, M files` on stdout

## Phase 2: Fast Lookup (1pt)
- `scripts/search/find-symbol.sh <name> [--kind <kind>] [--repo <repo>]`
  - Primary path: `jq` line filter (sub-millisecond on 22k-record index)
  - Fallback: `grep -F | uv run --no-project python` for systems without jq
  - Exit 0 on hit, exit 1 + "Symbol not found" on miss

## Phase 3: Cross-Repo Search (2pts)
- `scripts/search/cross-repo-search.sh <pattern> [--type <ext>] [--repo <name>]`
  - Prefer `rg` (ripgrep); fall back to `grep -r` with warning
  - Ranked output: `src/` hits first, then `tests/`, then `docs/`
  - Prefix each line with `repo:` for unambiguous location

## Phase 4: Hook Integration (1pt)
- Extend `scripts/hooks/post-merge`
  - Check `git diff HEAD@{1} HEAD --name-only | grep -q '^<repo>/src/'`
  - Trigger `build-symbol-index.py --quiet` only when src/ changed

## Phase 5: Tests (2pts)
- `tests/search/test-symbol-index.sh` — bash integration tests
  - T1: build produces ≥50 records
  - T2: find-symbol returns hits for known symbol
  - T3: find-symbol exits 1 on miss
  - T4: cross-repo-search returns ranked hits
  - T5: broken .py file is skipped, not fatal
  - T6: --kind filter narrows results
  - T7: --repo filter narrows results
  - T8: --type filter narrows search

## Test Strategy
- All 8 tests must PASS, 0 FAIL
- `bash tests/search/test-symbol-index.sh` is the single entry point
- Cross-review via Codex (hard gate) + Gemini

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| rg not installed | grep -r fallback, printed warning |
| post-merge slowness | conditional rebuild (src/ diff check) |
| broken .py parse errors | graceful skip + warnings.warn |
| /work status integration | deferred stretch goal |
| index tracked in git → churn | gitignore config/search/symbol-index.jsonl; rebuild on demand |
| stale index from local edits | freshness check in find-symbol.sh warns when src/ newer than index |
| scope mismatch "all repos" | mission scoped to "five tier-1 Python repos" |

## Cross-Review Findings Resolution
- **MAJOR (Codex/Gemini)**: Tracked generated file → FIXED: .gitignore + git rm --cached
- **MAJOR (Codex)**: Freshness under-specified → FIXED: find-symbol.sh mtime check + warning
- **MAJOR (Codex)**: Scope mismatch → FIXED: mission language updated to "tier-1 Python repos"
- **MAJOR (Gemini)**: Python-only scope → ACCEPTED: this WRK targets Python; polyglot is follow-on
- **MAJOR (Gemini)**: TDD ordering → NOTED: retroactive WRK; future WRKs will test-first
- **MINOR (both)**: Test coverage gaps → DEFERRED: duplicate symbols, fallback paths added as follow-on WRK
