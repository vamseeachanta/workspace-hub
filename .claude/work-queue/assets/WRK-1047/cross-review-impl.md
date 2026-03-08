# WRK-1047 Cross-Review: Implementation

**Date**: 2026-03-08  
**Stage**: S13 (Agent Cross-Review)  
**Files reviewed**: scripts/readiness/harness-config.yaml, nightly-readiness.sh (WRK-1047 section),
compare-harness-state.sh, remediate-harness.sh, tests/work-queue/test-harness-readiness.sh

## Claude: REQUEST_CHANGES → RESOLVED
- P1: `_emit_harness_report` wrote `checks: {}` — FIXED: now emits per-check status+detail map
- P2: `check_r_hook_static` hardcoded blocking_patterns instead of reading harness-config.yaml — FIXED
- P2: `check_r_plugins` used substring match — FIXED: exact match with `(>|^)..(@|space|$)` pattern
- P2: `remediate-harness.sh` plugin name parsing tokenized all words — FIXED: parse after `missing:` prefix
- P3: `break` after first hook violation — FIXED: removed, all violations now reported
- P3: Missing `-e` in set flags for compare/remediate scripts — FIXED

## Codex: REQUEST_CHANGES → RESOLVED
- Same P1, P2a, P2b findings as Claude — all resolved (see above)

## Gemini: APPROVE
- P2 (global vars in `_emit_harness_report`): vars are defined in script scope before function call — OK
- P3 (sed -i portability): workspace is Linux-only per harness-config.yaml workstations — accepted
- P3 (brittle YAML parsers): noted as known limitation; acceptable for simple flat YAML config

## Post-fix Verdict
All P1 and P2 findings resolved. Test suite: 15 pass, 1 skip (T1 manual), 0 fail.
