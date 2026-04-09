---
title: "Closed Engineering Issues"
tags: [source, github-issues, engineering, closed]
type: closed-issues
ingested: 2026-04-09
---

# Source: Closed Engineering Issues

Key decisions and implementation approaches extracted from closed GitHub issues with the `cat:engineering` label.

## Issues Ingested

| Issue | Title | Closed | Wiki Page |
|-------|-------|--------|-----------|
| #1773 | DNV-RP-F105 pipeline free-span VIV fatigue module — clean-room | 2026-04-04 | [Free-Span VIV Fatigue](../concepts/free-span-viv-fatigue.md), [DNV-RP-F105](../standards/dnv-rp-f105.md) |
| #1791 | Probability-weighted multi-current damage summation | 2026-04-04 | [Free-Span VIV Fatigue](../concepts/free-span-viv-fatigue.md) |
| #1768 | OrcaWave-to-OrcaFlex handoff pipeline | 2026-04-04 | [OrcaWave-to-OrcaFlex Pipeline](../workflows/orcawave-to-orcaflex-pipeline.md) |
| #1984 | Seakeeping module — 6-DOF motion analysis | 2026-04-06 | [Seakeeping and 6-DOF Ship Dynamics](../concepts/seakeeping-6dof.md) |
| #1858 | Field-dev FDAS + economics integration | 2026-04-09 | [Field Development Economics](../concepts/field-development-economics.md) |

## Key Themes

- **Clean-room implementation**: When legacy code has copyright constraints, build from published standards only (#1773)
- **Automation of manual pipelines**: Replace multi-step manual processes with single-command workflows (#1768)
- **Probability-weighted methods**: Real engineering assessments require summation across environmental bins, not single deterministic runs (#1791)
- **Cross-repo integration**: Wire existing calculation libraries from satellite repos into the main digitalmodel package (#1858)
