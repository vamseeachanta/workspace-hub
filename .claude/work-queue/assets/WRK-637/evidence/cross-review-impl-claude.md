# Cross-Review — WRK-637 Implementation (Claude)

**Stage**: 13 — Agent Cross-Review (Implementation)
**Provider**: Claude Sonnet 4.6
**Verdict**: APPROVE (after fixes applied)

## Summary

Initial review returned REQUEST_CHANGES on 4 findings. All 4 resolved in Stage 13.

## Findings

### P1 — Security: shell=True command injection
- **Severity**: P1 (security gate)
- **Location**: `compact-memory.py` — `_spot_check_command()`
- **Issue**: `subprocess.run(stripped, shell=True, ...)` allows injection via crafted bullet content
- **Resolution**: Removed `shell=True`; split cmd with `.split()`; added `_SAFE_CMD_PREFIXES` allowlist and `_UNSAFE_PATTERNS` regex; unknown/unsafe commands return `True` (conservative keep)
- **Status**: FIXED ✓

### P2 — Path staleness cross-machine false positives
- **Severity**: P2 (correctness)
- **Location**: `compact-memory.py` — Rule 2 in `audit()`
- **Issue**: `os.path.exists()` on machine A produces false positives for paths valid on machine B; consistent with `--check-commands` opt-in pattern
- **Resolution**: Rule 2 now gated behind `--check-paths` flag; `check_paths=False` default
- **Status**: FIXED ✓

### P2 — `# keep` asymmetric scope undocumented
- **Severity**: P2 (documentation)
- **Location**: `compact-memory.py` — module docstring
- **Issue**: `# keep` exempts rules 4-5 (dedup, trim) but NOT rules 1-2; intentional by design but not documented
- **Resolution**: Added `# keep marker scope` section to module docstring explaining asymmetric behaviour and rationale
- **Status**: FIXED ✓

### P3 — curate-memory.py test coverage thin
- **Severity**: P3 (quality)
- **Location**: `tests/memory/test_curate_memory.py`
- **Issue**: Only 5 tests; missing: keep marker, archive classification, missing-root error path
- **Resolution**: Added T6 (keep marker → memory-keep), T7 (done-WRK → archive), T8 (missing root exits non-zero)
- **Status**: FIXED ✓

## Final Verdict

**APPROVE** — all P1/P2/P3 findings resolved. 21 tests pass.
