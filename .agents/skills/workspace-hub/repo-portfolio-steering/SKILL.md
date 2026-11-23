---
name: repo-portfolio-steering
description: Generate a one-page portfolio steering report for workspace-hub. Use
  when the user invokes /repo-portfolio-steering, asks about harness vs engineering
  balance, wants a portfolio health check, or asks which repos to fund next. Reports
  on portfolio steering, GTM readiness, and provider activity balance.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
harness_threshold: 0.3
capabilities:
- harness_balance_check
- gtm_readiness_ranking
- provider_activity_analysis
- next_actions_recommendation
tools:
- Read
- Bash
- Glob
related_skills:
- comprehensive-learning
scripts:
- scripts/skills/repo-portfolio-steering/compute-balance.py
requires: []
tags: []
---

# repo-portfolio-steering Skill

> One-page portfolio steering report: harness/engineering balance, GTM-readiness ranking,
> per-provider agentic activity, and the next 3 highest-leverage actions to fund.

## Quick Start

```bash
# Full steering report (run from workspace-hub root)
uv run --no-project python scripts/skills/repo-portfolio-steering/compute-balance.py

# Custom threshold
uv run --no-project python scripts/skills/repo-portfolio-steering/compute-balance.py --threshold 0.25

# With portfolio signals (Layer 2)
uv run --no-project python scripts/skills/repo-portfolio-steering/compute-balance.py \
  --signals .claude/state/portfolio-signals.yaml
```

## 5 Output Sections

### Section 1 — Balance Snapshot (L1)

Reads `## By Category` summary table from `INDEX.md`.

| Category | Count | % | Status |
|----------|-------|---|--------|
| harness  | N     | N% | ✓ / ⚠ |
| engineering | N  | N% | —     |

**Threshold**: `harness_threshold` in frontmatter (default 30%).
- ≤ threshold → `HEALTHY`
- > threshold → `OVER-INVESTED`

### Section 2 — Harness Saturation Signal

**Layer 1 — Queue balance** (from INDEX.md):
- Default threshold: 30% configurable via `HARNESS_THRESHOLD`
- Output: `HEALTHY` or `OVER-INVESTED` + recommended max harness items before returning to engineering

**Layer 2 — Agentic activity by provider** (from `.claude/state/portfolio-signals.yaml`):

```
Provider | Harness (30d) | Engineering (30d) | Harness%
claude   | 4             | 3                 | 57% ⚠ OVER
codex    | 1             | 5                 | 17% ✓
gemini   | 0             | 2                 | 0%  ✓
```

Source: `portfolio-signals.yaml` `provider_activity` section.
If file is absent, Layer 2 is skipped (graceful degradation).

**Layer 3 — Capability research** (deferred to WRK-1020):
`capability_signals` key will be added by the nightly cron without breaking L1+L2.

### Section 3 — GTM-Ready Technical Capabilities

Ranks active engineering WRK items by demo-readiness:
- Rank criteria: `brochure_status` (ready > updated > draft > n/a)
- Secondary: `percent_complete` descending
- Tertiary: WRK ID ascending (older = more considered)

| WRK | Domain | Brochure | % Done | Demo Ready? |
|-----|--------|----------|--------|-------------|

### Section 4 — Next 3 Actions to Fund

Top 3 HIGH-priority engineering items mapped to GTM opportunities:

| WRK | Domain | Client Persona | Project Type | Action |
|-----|--------|---------------|--------------|--------|

Domain → Client Persona → Project Type mapping:

| Engineering Domain | Client Persona | Project Type |
|---|---|---|
| subsea pipeline / DNV RP F105 | Offshore operator / pipeline integrity engineer | VIV/freespan assessment |
| cathodic protection | Corrosion engineer / asset manager | CP system design report |
| marine / hydrodynamics | Naval architect / offshore designer | Motions & loads study |
| drilling / ROP models | Drilling engineer / well planner | Drilling performance analysis |
| production forecasting / Arps | Reservoir engineer / E&P consultant | Decline curve + reserves |
| net lease / CRE | Real estate investor / asset manager | NNN lease underwriting |
| structural / FEA | Structural engineer / EPC contractor | Plate/beam design check |

### Section 5 — Recommended Harness Budget

Spend-rate formula based on current `harness_pct`:

| harness_pct range | Budget rule |
|---|---|
| ≤ 15% | 1 harness per 3 engineering (ramp up harness) |
| 15%–30% | 1 harness per 5 engineering (maintain) |
| > 30% | 0 harness — pure engineering until below threshold |

## Runtime Inputs

| Input | Path | Purpose |
|---|---|---|
| Category View | `.claude/work-queue/INDEX.md` `## By Category` | Balance snapshot |
| WRK frontmatter | `pending/*.md` + `working/*.md` | brochure_status, category, priority |
| Portfolio signals | `.claude/state/portfolio-signals.yaml` | L2 provider activity + L3 capability |

## Session-Start Integration

This skill registers a **weekly steering mode** for `/session-start`:
- Trigger: user invokes `/repo-portfolio-steering` OR session-start detects `--mode weekly`
- Output replaces the "top items per category" summary with the full steering report
- No changes to session-start SKILL.md body — steering invoked as a delegate

## Acceptance Criteria

- [x] AC-1: SKILL.md at `.claude/skills/workspace-hub/repo-portfolio-steering/SKILL.md`
- [x] AC-2: Balance snapshot reads INDEX.md By Category
- [x] AC-3: Harness threshold default 30% + configurable
- [x] AC-4: GTM-readiness ranking by brochure_status + percent_complete
- [x] AC-5: Next 3 to fund maps domains to client personas
- [x] AC-6: Recommended harness budget outputs spend-rate
- [x] AC-7: Harness saturation signal includes per-provider activity (Layer 2)
- [x] AC-8: capability_signals key present does not crash (L3 compat)
- [x] AC-9: Missing portfolio-signals.yaml graceful (no crash)
- [x] AC-10: Session-start integration point documented
- [x] AC-11: Description triggers on portfolio/steering/harness phrases
