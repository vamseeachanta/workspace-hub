# Provider routing scorecard

Generated: 2026-05-19T20:16:43.565012Z
Current week: 2026-W21
Recommended provider order: gemini, codex, claude

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: underused
- Priority: high
- Current-week reported utilization: 2.9%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 36 / 1160
- Audit post records: 110989
- Missing repo reads: 8609
- Python3 per 1k records: 9.46
- Migration debt per 1k records: 15.53

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
- Current-week sessions / post records: 40 / 618
- Audit post records: 40631
- Missing repo reads: 1206
- Python3 per 1k records: 9.18
- Migration debt per 1k records: 0.47

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
- Quota basis: estimated_daily_quota (estimated)
- Current-week sessions / post records: 1 / 1
- Audit post records: 6198
- Missing repo reads: 602
- Python3 per 1k records: 46.95
- Migration debt per 1k records: 13.88

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

