---
name: todoist-api-upcoming-this-week-lenreportupcoming
description: 'Sub-skill of todoist-api: Upcoming This Week ({len(report[''upcoming''])}).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Upcoming This Week ({len(report['upcoming'])})

## Upcoming This Week ({len(report['upcoming'])})


"""
    for task in sorted(report["upcoming"], key=lambda t: t.due.date):
        content += f"- [ ] {task.content} (Due: {task.due.string})\n"

    content += f"""
