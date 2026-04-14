# Provider routing scorecard

Generated: 2026-04-14T09:20:04.143378Z
Current week: 2026-W16
Recommended provider order: gemini, codex, claude

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: underused
- Priority: high
- Current-week reported utilization: 0.6%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 9 / 233
- Audit post records: 74657
- Missing repo reads: 7560
- Python3 per 1k records: 8.63
- Migration debt per 1k records: 13.02

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
- Current-week reported utilization: 1.0%
- Quota basis: quota (history.jsonl)
- Current-week sessions / post records: 0 / 0
- Audit post records: 31413
- Missing repo reads: 0
- Python3 per 1k records: 10.16
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
- Current-week reported utilization: 0.0%
- Quota basis: estimated_daily_quota (estimated)
- Current-week sessions / post records: 1 / 1
- Audit post records: 5901
- Missing repo reads: 590
- Python3 per 1k records: 49.14
- Migration debt per 1k records: 14.23

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

