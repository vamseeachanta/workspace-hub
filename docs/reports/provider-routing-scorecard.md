# Provider routing scorecard

Generated: 2026-07-27T05:21:09.856563Z
Current week: 2026-W31
Recommended provider order: codex, agy, claude

This scorecard combines provider utilization with session-audit hygiene to decide where the next work packets should go.

## claude

- Status: underused
- Priority: high
- Current-week reported utilization: 0.0%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 0 / 0
- Audit post records: 123003
- Missing repo reads: 9463
- Python3 per 1k records: 9.12
- Migration debt per 1k records: 14.02

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
- Current-week reported utilization: 0.0%
- Quota basis: quota (history.jsonl-estimate)
- Current-week sessions / post records: 0 / 0
- Audit post records: 202717
- Missing repo reads: 1689
- Python3 per 1k records: 13.91
- Migration debt per 1k records: 0.05

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

## agy

- Status: underused
- Priority: highest
- Current-week reported utilization: 0.0%
- Quota basis: unavailable (unavailable)
- Current-week sessions / post records: 0 / 0
- Audit post records: 0
- Missing repo reads: 0
- Python3 per 1k records: 0.0
- Migration debt per 1k records: 0.0

### Preferred work
- batched research/recon
- risk enumeration
- competitor/standards scans
- issue expansion and scouting

### Avoid
- high-volume mechanical coding
- tight verification loops

### Recommended actions
- Batch 5-6 related research/recon tasks into agy sessions.
- Use agy for scouting/risk-analysis packets instead of leaving the lane idle.
- Telemetry is weak; treat utilization as directional, not exact weekly headroom.

