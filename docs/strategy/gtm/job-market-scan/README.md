# GTM: Job Market Scan

> Systematic scan of US job postings to identify consulting opportunities for ACE Engineer.

## Strategy

Every senior engineering job posting is a consulting lead. Companies hiring for OrcaFlex,
FEA, cathodic protection, riser/mooring engineering etc. have **budget, need, and urgency**.
A consulting engagement fills the gap faster than a 3-6 month hiring cycle.

## Sources & Compliance (Q9 / Q10 / Q11 — #1707, #2348)

Three live sources: **`linkedin`**, **`indeed`**, **`career_page`** (public company
career landings listed in `COMPANY_CAREER_URLS`).

Three **REMOVED** sources (Q9, 2026-04-21): `google`, `google_direct`, `rigzone` —
zero production results; not revisited without owner sign-off. The deletion is
recorded in the REMOVED appendix of [`TOS_REVIEW.md`](TOS_REVIEW.md).

- **robots.txt enforcement:** `urllib.robotparser` is consulted per destination
  netloc inside `safe_request()`. Unreachable robots.txt ⇒ **DENY** (fail-closed).
- **Owner override:** a source whose robots.txt disallows us can be retained only
  by a signed `Owner override:` block in [`TOS_REVIEW.md`](TOS_REVIEW.md) under
  the corresponding `## Source: <name>` heading. The scanner re-parses that file
  at each import; removing the block revokes the override on the next run.
  LinkedIn currently carries an owner override (Q11 KEEP decision).
- **Per-source owner sign-off (Q10):** every live source carries a datestamped
  `Owner approved: YYYY-MM-DD` line in [`TOS_REVIEW.md`](TOS_REVIEW.md). Adding a
  new source requires a new signed section before that source can scrape.
- **Cease-and-desist runbook (U4):** see [`TOS_REVIEW.md`](TOS_REVIEW.md) §
  *Cease-and-Desist Runbook* — 24h to takedown PR, 48h to incident record,
  7d to tracking issue.

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
- **Auto-commits** results to main after each scan, **only for sources whose ToS
  review is signed off by owner** in [`TOS_REVIEW.md`](TOS_REVIEW.md). Sources
  whose robots.txt denies us (without override) are silently skipped for that week.
- **Paused state**: the cron remains paused until all U1-U5 unpause criteria in
  the #2348 plan are green. See `config/scheduled-tasks/schedule-tasks.yaml`
  for the current disposition.

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
