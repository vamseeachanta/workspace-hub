---
name: gtm-job-market-scan
description: Scan job boards to identify consulting opportunities by matching hiring demand to a practitioner's capabilities. Build a GTM outreach campaign from job postings. Reusable scanner at scripts/gtm/job-market-scanner.py.
tags: [gtm, consulting, job-scan, outreach, email, linkedin, business-development]
triggers:
  - user wants to find consulting clients
  - user wants to scan job market for opportunities
  - user mentions go-to-market or GTM for services
  - user wants to identify companies hiring for their skills
---

# GTM Job Market Scan

Systematic scan of job boards to convert hiring demand into consulting leads.

## Core Thesis

Every senior engineering job posting is a consulting lead. Companies hiring FTEs at $150-250K+ have budget, need, and urgency. A consulting engagement fills the gap faster than a 3-6 month hiring cycle.

## Steps

### 1. Map the Practitioner's Capabilities

Before scanning, read the user's resume/CV and capability docs to extract:
- Exact tool names (OrcaFlex, ANSYS, COMSOL — these become search keywords)
- Domain keywords (subsea, mooring, cathodic protection, FEA)
- Standards knowledge (API 579, DNV, BS 7910 — niche = high value)
- Past clients (these become priority target companies)

Key files in workspace-hub:
- `teamresumes/cv/va_resume.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/strategy/engineering-chatbot-oilgas-pitch.md`
- `docs/research/engineering-capability-map.md`

### 2. Create GitHub Issues (Parent + Children)

Structure as a hierarchy:
- **Parent**: Broad US-wide scan across all verticals
- **Child 1**: Vertical-specific (e.g., vessel installation contractors)
- **Child 2**: Vertical-specific (e.g., energy companies)

Labels: `cat:strategy`, `domain:gtm`, `cat:business`
Cross-reference issues with comments on each.

Use `gh issue create --repo REPO --title "..." --label "..." --body '...'` with detailed markdown bodies including:
- Target company lists by tier
- Keyword search matrix
- Capability alignment matrix
- Phased deliverables with checkboxes
- Files to create
- Success criteria

### 3. Run the Scanner

```bash
# Full scan (all 22 keywords + 30 career pages)
/home/vamsee/miniforge3/bin/python scripts/gtm/job-market-scanner.py

# Limited scan (first N keywords, skip career pages)
/home/vamsee/miniforge3/bin/python scripts/gtm/job-market-scanner.py --limit 5 --skip-career-pages

# Custom keywords
/home/vamsee/miniforge3/bin/python scripts/gtm/job-market-scanner.py --keywords "OrcaFlex,mooring,cathodic protection"
```

### 4. Review and Prioritize Results

Auto-generated outputs:
- `docs/strategy/gtm/job-market-scan/dashboard.md` — summary stats
- `docs/strategy/gtm/job-market-scan/priority-targets.md` — ranked companies
- `docs/strategy/gtm/job-market-scan/raw-results/YYYY-MM-DD.json` — full data

Focus on "Hot Targets" = companies with 3+ matching open roles.

## Pitfalls

### Source Reliability (discovered through trial)
- **LinkedIn public search**: BEST source — returns 60+ results per keyword, no auth needed. Uses `linkedin.com/jobs/search/` with `sortBy=DD` and `f_TPR=r604800` (past week).
- **Indeed**: Blocks with 403 Forbidden ~80% of the time. Intermittently works. Don't rely on it.
- **Google Search**: Rate-limits aggressively (429 after ~5 requests). Only useful for first 3-4 keywords. Increase `REQUEST_DELAY` if needed.
- **Rigzone**: Returned 0 results in testing — site structure may have changed. Selectors need updating.
- **Company career pages**: Hit-or-miss. Some return useful listings (ABS: 30, Worley: 7), many return 0. Worth running but not primary source.

### Keyword Design
- Tier keywords by specificity: "OrcaFlex engineer" (maybe 50 people can do this) scores higher than "FEA analyst" (thousands can do this)
- Include location qualifiers for niche terms: "naval architect Houston"
- Broader terms (Tier 3-4) produce more noise but find manufacturing/aerospace opportunities

### Scoring
- Keyword tier: niche (Tier 1) = 80 points, broad (Tier 4) = 20 points
- Senior seniority: +30 points (they need experience NOW)
- Priority company: +25 points
- Houston location: +15 points
- Contract/consulting indicator in title: +20 points

### Python Environment
- Use `/home/vamsee/miniforge3/bin/python` (Python 3.13) — has requests + bs4
- NOT `python3` (system Python lacks bs4)
- NOT `uv run` for this script (it uses --no-project and deps aren't in any pyproject.toml)

### Git Workflow
- Check which branch you're on before committing (`git branch --show-current`)
- If on a feature branch, cherry-pick to main after committing — we hit this exact issue (committed to `feat/1668-harness-update-lifecycle` by accident, had to cherry-pick to main)
- Push to origin main explicitly
- The `weekly-scan-refresh.sh` wrapper handles this automatically (checks out main first)

### Test Runs Overwrite Raw Results
- Running `--limit 2 --skip-career-pages` to test overwrites `raw-results/YYYY-MM-DD.json` with partial data
- The cumulative index is safe (only adds, never removes), but the day's raw file is replaced
- If you need to preserve a full scan, copy the raw file before doing test runs on the same day

### Weekly Refresh Setup

The scanner is designed for repeated weekly runs with history tracking.

#### Cron Infrastructure
- **Cron task**: `gtm-job-market-scan` in `config/scheduled-tasks/schedule-tasks.yaml`
- **Schedule**: Monday 5AM UTC (`0 5 * * 1`)
- **Wrapper script**: `scripts/gtm/weekly-scan-refresh.sh` — pulls main, runs scanner, commits & pushes
- The wrapper auto-finds Python (miniforge → local → system fallback)

#### History Tracking (cumulative-index.json)
Each run compares results against `cumulative-index.json`:
- **New jobs**: first time seen → highlighted in `new-this-week.md`
- **Returning jobs**: seen before → `seen_count` incremented
- **Company history**: posting counts per company per scan date → feeds trend report

#### Auto-Generated Reports (refreshed each scan)
| Report | Value |
|--------|-------|
| `dashboard.md` | Overview stats, top companies, top jobs, seniority breakdown |
| `priority-targets.md` | Ranked companies by alignment score, hot targets (3+) |
| `new-this-week.md` | Delta — ONLY new postings since last scan (what to act on) |
| `trend-report.md` | 📈 Companies hiring MORE, 🔥 Persistent openings (consulting gold) |
| `cumulative-index.json` | All-time database of every posting ever seen |

#### Key Experiential Finding: Persistent Openings
> Jobs that appear in 2+ consecutive weekly scans are the **hardest to fill**.
> These persistent openings have the HIGHEST consulting conversion rate.
> The company has budget, has tried hiring, and STILL can't find someone.
> The trend report surfaces these automatically — prioritize outreach to them.

## Output Structure

```
docs/strategy/gtm/
├── job-market-scan/
│   ├── README.md
│   ├── dashboard.md            (auto-generated)
│   ├── priority-targets.md     (auto-generated)
│   ├── new-this-week.md        (auto-generated, weekly delta)
│   ├── trend-report.md         (auto-generated, week-over-week trends)
│   ├── cumulative-index.json   (all-time job tracking DB)
│   ├── raw-results/
│   │   └── YYYY-MM-DD.json
│   ├── keyword-results/
│   └── company-profiles/
└── vessel-installation-contractors/  (vertical-specific)

scripts/gtm/
├── job-market-scanner.py
└── weekly-scan-refresh.sh      (cron wrapper)
```

## Integration with aceengineer-strategy Repo

The scanner is a DATA SOURCE — results must flow into the aceengineer-strategy private repo which is the GTM command center.

### Key aceengineer-strategy files to update after each scan:
- `pipeline/prospects.md` — add new high-scoring companies
- `pipeline/scanner-hot-targets.md` — refresh with latest scan rankings
- `pipeline/job-scan-integration.md` — cross-reference scanner → existing prospects
- `strategy/go-to-market.md` — update Evolution Log with scan findings
- `metrics/weekly-scorecard.md` — update "prospects contacted" as outreach happens

### Email Templates (created, ready for personalization)
- `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` — 3-step sequence (Day 0/3/7)
- `docs/strategy/gtm/job-market-scan/email-templates-by-vertical.md` — 5 vertical variants with {{PLACEHOLDERS}}

Verticals: installation, cathodic protection, FEA/manufacturing, offshore wind, classification societies.

### Conference Prep (lives in aceengineer-strategy)
- `pipeline/conference-prep-q2-2026.md` — master Q2 action plan
- `pipeline/otc-2026-meeting-requests.md` — 10 companies × 3 message variants

### Parallel Execution Pattern
When executing the full GTM cycle, run 4 workstreams in parallel via subagents:
1. Full scan (background terminal — ~10 min)
2. Strategy repo cross-linking (subagent — reads prospects, creates integration docs)
3. Email template drafting (subagent — uses positioning/pricing from strategy repo)
4. Conference prep (subagent — creates action plan with dated checklists)

No git contention: WS-1 writes workspace-hub/docs/strategy/gtm/, WS-2-4 write aceengineer-strategy/pipeline/.

Run P0 expansions in parallel via 3 subagents (one per package). Each subagent gets:
- Existing module listing + __init__.py exports
- Test file listing
- AGENTS.md conventions (test command, src layout)
- Specific new modules to create with engineering standard references
- Instruction to commit from within digitalmodel/ dir (separate git repo)

### Demo Scripts as Sales Collateral

After expanding packages, create self-contained demo scripts at `examples/demos/`:
- Each demo imports actual library modules and runs real calculations
- Print results in a clean, impressive terminal format
- Include header: "ACE Engineer — [capability]" and footer with contact info
- Test that each runs: `PYTHONPATH=src uv run python examples/demos/demo_xxx.py`
- Demos become email attachments / GitHub links for prospect outreach

## First Scan Baseline (2026-04-02)

- 708 jobs, 460 companies, 22 keywords (full run with history tracking)
- LinkedIn produced ~85% of results (best source by far)
- 121 senior roles, 25 hot targets with 3+ roles each
- Top hits: Oceaneering (11), WSP (12), ABS (9), Jacobs (9), Orsted (6)
- Key discovery: LNG sector was a blind spot (Venture Global, Cheniere both scored high)
- Key discovery: Oceaneering was under-tiered in prospect list (11 roles = Tier 1)

### Package Expansion Results (P0 + P1, 2026-04-02)

| Package | Before | After | Growth | Tests |
|---------|--------|-------|--------|-------|
| cathodic_protection | 5 | 17 | +12 | 198 ✅ |
| ansys | 5 | 15 | +10 | 324 ✅ |
| fatigue | 7 | 16 | +9 | 241 ✅ |
| orcaflex | 14 | 25 | +11 | 148 (created) |
| orcawave | 13 | 20 | +7 | 70 (created) |
| **TOTAL** | **44** | **93** | **+49** | **763+ passed** |

3 demo scripts created: `demo_sn_library.py`, `demo_pressure_vessel.py`, `demo_pipeline_cp.py`
