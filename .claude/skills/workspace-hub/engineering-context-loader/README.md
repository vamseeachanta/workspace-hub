# engineering-context-loader

Auto-detects the active engineering domain from a WRK item's `tags:` field
and outputs a focused context: relevant skills to load, applicable design
codes, and domain-specific memory/spec files.

## Trigger

```
/engineering-context-loader
```

Also run manually after `/session-start` when the active WRK item has
engineering domain tags.

## Quick Start

1. Run `/session-start` to get the briefing and top unblocked WRK items.
2. Run `/engineering-context-loader` — it reads the active WRK item's tags.
3. Read the listed SKILL.md files before starting implementation work.

## Active WRK Resolution

| Priority | Source |
|----------|--------|
| 1 | `.claude/state/active-wrk` (explicit state file) |
| 2 | Most recently modified `work-queue/working/*.md` |
| 3 | Git branch name (e.g. `feature/WRK-175-...`) |
| 4 | Prompt user for WRK ID |

## Supported Domains

| Tag | Skills Loaded | Design Codes |
|-----|--------------|--------------|
| `mooring` | mooring-design, orcaflex-mooring-iteration, hydrodynamics | API RP 2SK, DNV-OS-E301 |
| `fatigue` | fatigue-analysis, signal-analysis, orcaflex-post-processing | DNV-RP-C203, BS 7608 |
| `riser` | catenary-riser, viv-analysis, structural-analysis | API RP 2RD, DNV-ST-F201 |
| `hull` | hydrodynamics, diffraction-analysis, orcawave-analysis | DNV-OS-C105 |
| `pipeline` | structural-analysis, orcaflex-modeling | DNV-ST-F101, API RP 1111 |
| `structural` | structural-analysis, orcaflex-code-check | API RP 2A, ISO 19902 |
| `cp` / `cathodic-protection` | cathodic-protection | DNV-RP-B401 |
| `drilling` | api12-drilling-analyzer | API TR 5C3 |
| `energy-economics` / `field-development` | fdas-economics, field-analyzer | N/A |
| `portfolio` / `investments` | data-management, plotly-visualization | N/A |

Multiple domains are supported in one WRK item — the skill outputs the union
of all matched skills and codes.

## Full Documentation

See `SKILL.md` for the complete step-by-step logic, path resolution table,
output format, and error-case handling.
