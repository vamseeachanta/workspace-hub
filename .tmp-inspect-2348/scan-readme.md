# GTM: Job Market Scan

> Systematic scan of US job postings to identify consulting opportunities for ACE Engineer.

## Strategy

Every senior engineering job posting is a consulting lead. Companies hiring for OrcaFlex,
FEA, cathodic protection, riser/mooring engineering etc. have **budget, need, and urgency**.
A consulting engagement fills the gap faster than a 3-6 month hiring cycle.

## Scanner

```bash
# Full scan (first time or ad-hoc)
python scripts/gtm/job-market-scanner.py

# Weekly refresh (with history tracking — used by cron)
python scripts/gtm/job-market-scanner.py --refresh

# Quick scan (subset of keywords)
python scripts/gtm/job-market-scanner.py --limit 5 --skip-career-pages

# Specific keywords only
python scripts/gtm/job-market-scanner.py --keywords "OrcaFlex engineer,mooring engineer"
```

## Weekly Refresh (Automated)

- **Schedule:** Every Monday 5AM UTC
- **Cron task:** `gtm-job-market-scan` in `config/scheduled-tasks/schedule-tasks.yaml`
- **Wrapper:** `scripts/gtm/weekly-scan-refresh.sh`
- **Auto-commits** results to main after each scan

### What the weekly refresh tracks:
- **New postings** not seen in any previous scan
- **Returning postings** (persistent = hard to fill = consulting gold)
- **Company hiring trends** — who is hiring MORE over time
- **Cumulative index** — all-time database of every posting seen

## Related Issues

- #1671 — US-Wide Job Market Scan (parent)
- #1670 — Energy Company Scan
- #1669 — Vessel Installation Contractor Outreach

## Output Files

| File | Purpose | Git-tracked? |
|------|---------|-------------|
| `dashboard.md` | Summary dashboard (auto-generated) | ✅ |
| `priority-targets.md` | Ranked target list (auto-generated) | ✅ |
| `new-this-week.md` | Delta from last scan — NEW postings only | ✅ |
| `trend-report.md` | Week-over-week hiring momentum | ✅ |
| `cumulative-index.json` | All-time job tracking database | ✅ |
| `raw-results/YYYY-MM-DD.json` | Raw scan data per run | ✅ |
| `keyword-results/` | Per-keyword aggregated results | ✅ |
| `company-profiles/` | Hot company deep-dives | ✅ |
