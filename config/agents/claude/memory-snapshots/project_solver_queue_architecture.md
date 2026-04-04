---
name: Solver queue architecture — operational with production features
description: Git-based pull queue for OrcaWave/OrcaFlex on licensed-win-1 — batch submission, retry logic, results dashboard, watch-results cron all live
type: project
---

Solver dispatch uses a git-based pull queue, NOT SSH push from dev-primary. **Status: PRODUCTION** as of 2026-04-02.

**Why:** Corporate firewall blocks inbound SSH to licensed-win-1. Outbound git access to GitHub works fine.

**Core infrastructure (2026-03-30 to 2026-03-31):**
- Queue dirs: `queue/pending/`, `queue/completed/`
- Task Scheduler live on ACMA-ANSYS05 (30-min polling)
- dev-primary commits job requests → licensed machine polls → runs OrcaWave/OrcaFlex → commits results

**Production features added 2026-04-01 to 2026-04-02:**
- Batch submission with YAML manifest + schema validation CLI (#1595, #1650)
- Retry logic with exponential backoff for failed jobs (#1654)
- Result watcher + post-processing hook + queue health monitoring (#1586)
- Results dashboard + cron integration for watch-results (#1648)

**How to apply:** To submit a solver job, commit a job spec to `queue/pending/` (or use batch submission with YAML manifest). Verify input files are git-tracked before submitting (see feedback_queue_git_tracked.md). Phase 07-03 is the final go/no-go gate: round-trip verification with L00/L01 benchmarks.
