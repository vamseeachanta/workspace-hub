# Provider routing scorecard

Generated: 2026-06-24T21:20:42.458406Z
Current week: 2026-W26
Recommended provider order: gemini, claude, codex

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: underused
- Priority: high
- Current-week reported utilization: 0.0%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 0 / 0
- Audit post records: 119505
- Missing repo reads: 9448
- Python3 per 1k records: 9.0
- Migration debt per 1k records: 14.43

### Preferred work
- adversarial plan review
- adversarial implementation review
- long-context synthesis
- complex repo strategy and architecture

### Avoid
- bounded test-fix loops
- mechanical refactors
- commodity grep/read sweeps

### Recommended actions
- Reserve Claude for adversarial review, plan review, and long-context synthesis.
- Do not burn Claude on mechanical loops that Codex can absorb.
- Reduce stale-path drift before increasing provider load; wasted reads are burning credits.
- Telemetry is weak; treat utilization as directional, not exact weekly headroom.

## codex

- Status: needs_cleanup
- Priority: high
- Current-week reported utilization: 40.0%
- Quota basis: quota (local-session-rate-limits)
- Current-week sessions / post records: 54 / 6023
- Audit post records: 121856
- Missing repo reads: 1690
- Python3 per 1k records: 17.64
- Migration debt per 1k records: 0.08

### Preferred work
- bounded implementation
- test writing and repair
- mechanical cleanup/refactors
- issue execution with crisp scope

### Avoid
- large open-ended research
- broad ecosystem synthesis

### Recommended actions
- Route bounded implementation/test/refactor issues to Codex immediately.
- Use Codex for repetitive repo-hardening tasks before spending more Claude review cycles.
- Reduce stale-path drift before increasing provider load; wasted reads are burning credits.

## gemini

- Status: underused
- Priority: highest
- Current-week reported utilization: 0.0%
- Quota basis: quota (manual-snapshot)
- Current-week sessions / post records: 0 / 0
- Audit post records: 6210
- Missing repo reads: 615
- Python3 per 1k records: 46.86
- Migration debt per 1k records: 13.85

### Preferred work
- batched research/recon
- risk enumeration
- competitor/standards scans
- issue expansion and scouting

### Avoid
- high-volume mechanical coding
- tight verification loops

### Recommended actions
- Batch 5-6 related research/recon tasks into Gemini sessions.
- Use Gemini for scouting/risk-analysis packets instead of leaving the lane idle.

