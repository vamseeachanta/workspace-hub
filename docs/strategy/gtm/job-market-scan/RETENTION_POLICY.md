# GTM Job Market Scan Retention Policy

Status: Active
Issue: #1709

## Purpose
Keep GTM scan outputs useful for trend analysis without allowing the repository to grow unbounded.

## Policy
- Keep tracked raw scan results in `docs/strategy/gtm/job-market-scan/raw-results/` for 12 weeks maximum.
- Move older raw scan result JSON files into the gitignored local archive directory:
  - `docs/strategy/gtm/job-market-scan/archive/`
- Keep cumulative scan metadata and company history in `cumulative-index.json`, but prune scan-history and company-history entries older than 6 months.
- Preserve current summary artifacts in git:
  - `cumulative-index.json`
  - `new-this-week.md`
  - `dashboard.md`
  - `priority-targets.md`
  - `trend-report.md`

## Operational Notes
- Archive files are machine-local and intentionally gitignored.
- Retention enforcement runs automatically from `scripts/gtm/job-market-scanner.py` after each refresh.
- If a longer-term historical study is needed, export archive data outside the repo before pruning windows are adjusted.
