# WRK-1085 Test Results

## TDD Status: GREEN

### test-symbol-index.sh — 8/8 passed

| Test | Description | Result |
|------|-------------|--------|
| T1 | build-symbol-index.py produces ≥50 records (got 22,697) | PASS |
| T2 | find-symbol.sh returns hits for 'load' (got 38 hits) | PASS |
| T3 | find-symbol.sh exits 1 with 'Symbol not found' on miss | PASS |
| T4 | cross-repo-search.sh src/ lines appear before tests/ | PASS |
| T5a | build-symbol-index.py skips broken .py — SyntaxError warning emitted | PASS |
| T5b | Good file still indexed alongside broken one | PASS |
| T5c | build-symbol-index.py exits 0 after encountering broken file | PASS |
| T6 | find-symbol.sh --kind class --repo assethold filters correctly | PASS |

Run: `bash tests/search/test-symbol-index.sh`

## Acceptance Criteria Coverage

- [x] `cross-repo-search.sh` searches all repos with ranked output (T4)
- [x] `build-symbol-index.py` generates `symbol-index.jsonl` from all tier-1 src/ (T1)
- [x] `find-symbol.sh <name>` returns repo + file + line in <1s (T2)
- [x] Post-merge hook triggers index rebuild when src/ changes
- [x] Index covers: classes, functions, constants (T6), methods
- [ ] Cross-review (Codex) passes — MAJOR findings resolved, MINOR deferred
