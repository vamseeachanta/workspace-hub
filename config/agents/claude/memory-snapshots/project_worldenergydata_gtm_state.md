---
name: worldenergydata GTM state
description: GTM execution state for worldenergydata — what's done, what's ready to send to clients, and what's blocked
type: project
originSessionId: eeda8a41-16c1-49a7-a086-2a0f25db1b88
---
As of 2026-05-04, all key worldenergydata GTM deliverables are committed on branch `docs/handoff-2026-05-03-lt-epic-closed` in the `worldenergydata` repo.

**Why:** GTM review pass driven from workspace-hub issue #117.

**How to apply:** When user asks about worldenergydata GTM status or wants to share materials with clients, point to these artifacts.

## Ready-to-send client reports

| File | Size | Audience |
|------|------|---------|
| `reports/gtm/2026-05-04-fdas-field-development-economics.html` | 63 KB | E&P engineers, project finance |
| `reports/gtm/2026-05-04-gtm-production-decline-forecast.html` | 4.8 MB | Petroleum engineers, asset managers |
| `reports/gtm/2026-05-04-bsee-field-analysis-comprehensive.html` | 90 KB | GoM deepwater operators, reservoir engineers, asset managers |
| `notebooks/gtm_production_decline_forecast.ipynb` | 4.8 MB | Share on LinkedIn |
| `reports/IMO_GISIS_Executive_Report.html` | 133 KB | Marine ops, HSE leads |
| `reports/bsee/lower_tertiary/lt_executive_summary.html` | 515 KB | GoM deepwater operators |

## Latest report: BSEE Comprehensive Field Analysis (commit `d8706964`)
- 90 KB self-contained HTML with 6 interactive Plotly charts
- Covers all 10 Lower Tertiary fields: NPV, IRR, MIRR, payback, breakeven, 5-point sensitivity
- Operator benchmarking table (Chevron, BP, Shell, TotalEnergies, Equinor, Beacon)
- Per-field detail cards with inline sensitivity tables
- Generation script: `scripts/gtm/generate_bsee_field_analysis_report.py`
- Format incorporates aceengineercode legacy patterns: KPI card grid, sticky tables, 5-pt sensitivity

## Critical fix landed (commit `08943965`)
BSEE import hang fixed: 17 files, module-level singletons moved to class `__init__`. `import worldenergydata.bsee` now 0.03s (was 30+ seconds). Worldenergydata issue #384 closed.

## Module readiness (all import in 2.1s total)
- FDAS Economics: Ready ✅
- Arps Decline / Production Forecast: Ready ✅
- Marine Safety / IMO GISIS: Ready ✅
- Lower Tertiary Portfolio: Ready ✅
- BSEE Field Analysis: Unblocked ✅ (was blocked by import hang)
- Pipeline Safety: Data-only (needs PHMSA download)

## Open issues
- workspace-hub #2640: production decline notebook — DONE
- worldenergydata #384: BSEE lazy-load — DONE
- workspace-hub #2003: 2 failing tests (performance + hypothesis edge case, pre-existing)
- workspace-hub #2005: collection timeout (32K orphan bytecode files, separate cleanup)
- workspace-hub #2346: prospect-data pipeline (plan-approved, needs run_demo() impl)

## uv run first-run warning
First `uv run` compiles 32K bytecode files (~4.5 min). Use `.venv/bin/python` directly for scripts in worldenergydata to avoid this.
