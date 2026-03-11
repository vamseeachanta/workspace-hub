# WRK-1123 Cross-Review Results

## Summary

Three-pass cross-review (Claude, Codex, Gemini) of `start_stage.py` guard changes.

## Claude Verdict: REQUEST_CHANGES → APPROVE (after fixes)

### P1 Fixed: PermissionError in _maybe_purge_stale_lock
`os.kill(pid, 0)` raises `PermissionError` (EPERM) when process IS alive but owned by
a different user. Catching it with `ProcessLookupError` caused live locks to be purged.
Fix: separate `except PermissionError: return` branch.

### P2 Fixed: Duplicate guard body for stage >= 9
The `stage >= 9` path duplicated the `working/` check inline instead of calling
`_stage1_working_guard()`. Consolidated to call the shared helper.

## Codex Verdict: REQUEST_CHANGES (pre-existing issues, not introduced here)
- P1: wrk_id path traversal (pre-existing, FW-1)
- P2: Brittle YAML fallback parser (pre-existing, FW-2)

## Gemini Verdict: REQUEST_CHANGES (same pre-existing issues as Codex)

## Final Status: CLEAR for merge
New P1 fixed. Pre-existing findings deferred as FW-1/FW-2.
