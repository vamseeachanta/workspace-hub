---
name: time-tracking-hours-by-day
description: 'Sub-skill of time-tracking: Hours by Day.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Hours by Day

## Hours by Day


| Day | Hours |
|-----|-------|
"""

        for day, hours in report["toggl"]["by_day"].items():
            md += f"| {day} | {hours:.1f} |\n"

        md += "\n### Hours by Project\n\n"
        for project, hours in sorted(
            report["toggl"]["by_project"].items(),

*See sub-skills for full details.*
