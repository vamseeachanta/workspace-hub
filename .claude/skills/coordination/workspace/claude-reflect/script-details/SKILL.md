---
name: claude-reflect-script-details
description: 'Sub-skill of claude-reflect: Script Details (+1).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Script Details (+1)

## Script Details


| Script | Phase | Input | Output |
|--------|-------|-------|--------|
| `analyze-history.sh` | REFLECT | Git repos | `analysis_*.json` |
| `extract-patterns.sh` | ABSTRACT | Analysis JSON | `patterns_*.json` |
| `analyze-trends.sh` | GENERALIZE | Multiple patterns | `trends_*.json` |
| `create-skills.sh` | STORE | Patterns | Skills + learnings |
| `generate-report.sh` | Report | All data | `weekly_digest_*.md` |

## Output Locations


```
~/.claude/state/
├── reflect-state.yaml       # Current state
├── reflect-history/         # Raw analysis files
│   └── analysis_*.json
├── patterns/                # Extracted patterns
│   └── patterns_*.json
├── trends/                  # Trend analysis
│   └── trends_*.json
└── reports/                 # Weekly digests

*See sub-skills for full details.*
