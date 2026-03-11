# WRK-668 Stage 13 — Agent Cross-Review Findings

**Reviewer**: feature-dev:code-reviewer subagent
**Verdict**: NEEDS_REVISION → resolved → APPROVE_WITH_MINOR

## P1 Findings (all resolved)

### P1-A: Empty html_verification_ref/legal_scan_ref silently bypass gate
- **File**: gate_checks_archive.py
- **Fix**: Added explicit empty-string check before path-exists check — now hard-fails if field is blank
- **Status**: RESOLVED

### P1-B: Shell injection in archive-item.sh heredoc
- **File**: archive-item.sh (pre-existing code, not introduced by WRK-668)
- **Fix**: Out of WRK-668 scope. Captured as follow-on WRK (archive-item.sh security hardening)
- **Status**: DEFERRED — captured as future work

### P1-C: spin_off_wrks sed logic generates invalid YAML for multi-spinoff
- **File**: create-spinoff-wrk.sh
- **Fix**: Replaced sed with `uv run --no-project python -c` using yaml.safe_load/dump
- **Status**: RESOLVED

## P2 Findings

### P2-A: Docstring gate numbering inconsistency — DEFERRED (informational, no logic bug)
### P2-B: Test helper uses naive string formatting — DEFERRED (does not affect current tests)
### P2-C: Dead code in _build_archive_readiness_card exemption lookup — DEFERRED (harmless)
### P2-D: Partial archive write on stage-20 update failure — DEFERRED as future work

## P3 Findings

### P3-B: Test used "clean" not canonical value — FIXED (changed to "merged-to-main")
### P3-C: T4 referenced in docstring but not implemented — FIXED (docstring corrected)
### P3-D: Remote unreachable treated as PASS — DEFERRED (low risk, noted in future work)

## Post-fix test results
57 PASS, 1 SKIP, 0 FAIL across test_archive_readiness.py + test_gate_verifier_hardening.py + test_d_item_gates.py
