---
name: skills-curation-phase-6-yield-tracking-and-cadence-adjustment
description: "Sub-skill of skills-curation: Phase 6 \u2014 Yield Tracking and Cadence\
  \ Adjustment."
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Phase 6 — Yield Tracking and Cadence Adjustment

## Phase 6 — Yield Tracking and Cadence Adjustment


After each run, record yield and adjust cadence:

**Yield metrics:**

```yaml
yield:
  skills_created: <N>      # new skill stubs created this run
  skills_updated: <N>      # existing skills enhanced
  wrk_items_created: <N>   # deep gap WRK items spun off
  research_findings: <N>   # total research results processed
  gaps_closed: <N>         # skills_created + stubs filled
```

**Cadence adjustment logic:**

```
YIELD_THRESHOLD_HIGH = 5   # findings per run
YIELD_THRESHOLD_LOW  = 1

consecutive_low_runs counter:
  if yield < YIELD_THRESHOLD_LOW for 3 consecutive runs:
    step down cadence:  weekly → biweekly → monthly
  if yield >= YIELD_THRESHOLD_HIGH:
    step up cadence:    monthly → biweekly → weekly
    reset consecutive_low_runs = 0
```

Cadence is written back to `curation-log.yaml` after each run.

---
