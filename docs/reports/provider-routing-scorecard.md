# Provider routing scorecard

Generated: 2026-05-08T05:20:04.624290Z
Current week: 2026-W19
Recommended provider order: gemini, codex, claude

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: needs_cleanup
- Priority: high
- Current-week reported utilization: 5.1%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 38 / 2058
- Audit post records: 104285
- Missing repo reads: 8818
- Python3 per 1k records: 8.82
- Migration debt per 1k records: 16.68

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
- Current-week reported utilization: 2.6%
- Quota basis: quota (history.jsonl)
- Current-week sessions / post records: 11 / 1154
- Audit post records: 30827
- Missing repo reads: 730
- Python3 per 1k records: 11.84
- Migration debt per 1k records: 2.3

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
- Current-week reported utilization: 0.1%
- Quota basis: estimated_daily_quota (estimated)
- Current-week sessions / post records: 2 / 2
- Audit post records: 6185
- Missing repo reads: 604
- Python3 per 1k records: 47.05
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

