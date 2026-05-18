# Provider routing scorecard

Generated: 2026-05-18T05:20:06.256726Z
Current week: 2026-W21
Recommended provider order: gemini, codex, claude

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: underused
- Priority: high
- Current-week reported utilization: 1.0%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 22 / 418
- Audit post records: 105154
- Missing repo reads: 8824
- Python3 per 1k records: 9.69
- Migration debt per 1k records: 16.54

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
- Current-week reported utilization: 1.1%
- Quota basis: quota (history.jsonl)
- Current-week sessions / post records: 0 / 0
- Audit post records: 31761
- Missing repo reads: 818
- Python3 per 1k records: 11.49
- Migration debt per 1k records: 2.24

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
- Current-week reported utilization: 0.0%
- Quota basis: estimated_daily_quota (estimated)
- Current-week sessions / post records: 0 / 0
- Audit post records: 6189
- Missing repo reads: 604
- Python3 per 1k records: 47.02
- Migration debt per 1k records: 13.9

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

