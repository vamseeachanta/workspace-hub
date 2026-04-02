# GTM: Job Market Scan

> Systematic scan of US job postings to identify consulting opportunities for ACE Engineer.

## Strategy

Every senior engineering job posting is a consulting lead. Companies hiring for OrcaFlex,
FEA, cathodic protection, riser/mooring engineering etc. have **budget, need, and urgency**.
A consulting engagement fills the gap faster than a 3-6 month hiring cycle.

## Scanner

Run: `uv run --no-project python scripts/gtm/job-market-scanner.py`

## Related Issues

- #1671 — US-Wide Job Market Scan (parent)
- #1670 — Energy Company Scan
- #1669 — Vessel Installation Contractor Outreach

## Output Files

- `raw-results/` — raw JSON from each scan run
- `keyword-results/` — per-keyword aggregated results
- `company-profiles/` — hot company deep-dives
- `dashboard.md` — summary dashboard (auto-generated)
- `priority-targets.md` — ranked target list (auto-generated)
