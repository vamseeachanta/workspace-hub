# Cross-Review — WRK-1049 Plan (Codex)

### Verdict: APPROVE

**Scope**: Three-file fix for concurrent claim collision.

**Assessment**:
- process.md change is correct and concise. Removing the mv bash snippet eliminates the bypass; the mandate to use claim-item.sh is unambiguous.
- start_stage.py lock write: uses `os.getpid()` which is the current Python process PID, not the Claude session PID. Acceptable as a signal — the main value is `hostname` + `locked_at` for human diagnosis, not automated liveness checks.
- claim-item.sh guard: `grep -E` pattern correctly targets all three fields. Exit 1 is fail-closed. Good.
- test-claim-collision.sh: uses real queue dir for T1/T4, which is correct since claim-item.sh uses `git rev-parse`. Trap cleanup prevents test pollution.

**No P1/P2 findings.**

[P3] The guard checks `working/WRK-NNN.md` presence only. A race window still exists between the guard check and the mv (TOCTOU). For a single-machine bash script this is acceptable — the window is sub-millisecond and concurrent Claude sessions are human-initiated.
