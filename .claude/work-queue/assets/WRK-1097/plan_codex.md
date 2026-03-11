# Codex Review — WRK-1097 Plan

## Verdict: REQUEST_CHANGES (High issues found)

### Issues Found

**HIGH: PID check fundamentally invalid**
- `session_pid` in session-lock.yaml stores `os.getpid()` from start_stage.py (a short-lived script)
- start_stage.py exits immediately after writing the lock → PID is always dead
- `kill -0 $pid` will ALWAYS return non-zero, making the "same host" liveness check false-negative-prone
- Fix: use age-based detection only; accept it as a heuristic (not PID-verified)

**MEDIUM: claimed/unclaimed classification ambiguous**
- claim-item.sh APPENDS a second `status:` key instead of updating in place
- Lock file has both `status: in_progress` and `status: claimed` — YAML parse result is implementation-dependent
- Fix: use queue location (working/ vs pending/) as canonical source of truth for claimed/unclaimed

**MEDIUM: Timing thresholds inconsistent**
- Plan says cross-machine fallback = 2h, but stale test = >4h
- 2h-4h range is unspecified → nondeterministic test behavior
- Fix: pick one threshold; define boundary behavior explicitly

### Suggestions
1. Remove PID check entirely from v1; ship age-only heuristic, document limitation
2. Canonical claimed/unclaimed = queue folder location (working/ vs pending/)
3. Single recency window: 2h for all cases; add boundary test at exactly 2h
4. Add end-to-end /whats-next test proving UNCLAIMED section is exclusive (item not in HIGH)

### Questions
- Should active-sessions.sh ship v1 as age-only with a FW item for heartbeat mechanism?
- Is queue location (pending/ vs working/) the canonical classification source?
- Should Stage 8 hard gate trigger at Stage 8 entry vs Stage 9 entry?
