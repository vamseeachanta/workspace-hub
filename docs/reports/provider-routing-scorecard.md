# Provider routing scorecard

Generated: 2026-04-24T21:20:06.092722Z
Current week: 2026-W17
Recommended provider order: codex, gemini, claude

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: needs_cleanup
- Priority: high
- Current-week reported utilization: 27.1%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 219 / 11020
- Audit post records: 89108
- Missing repo reads: 8454
- Python3 per 1k records: 8.53
- Migration debt per 1k records: 19.52

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

- Status: underused
- Priority: highest
- Current-week reported utilization: 0.2%
- Quota basis: quota (history.jsonl)
- Current-week sessions / post records: 188 / 2989
- Audit post records: 20144
- Missing repo reads: 463
- Python3 per 1k records: 17.92
- Migration debt per 1k records: 0.0

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

## gemini

- Status: underused
- Priority: highest
- Current-week reported utilization: 2.9%
- Quota basis: estimated_daily_quota (estimated)
- Current-week sessions / post records: 14 / 91
- Audit post records: 6173
- Missing repo reads: 603
- Python3 per 1k records: 47.14
- Migration debt per 1k records: 13.93

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
- Telemetry is weak; treat utilization as directional, not exact weekly headroom.

