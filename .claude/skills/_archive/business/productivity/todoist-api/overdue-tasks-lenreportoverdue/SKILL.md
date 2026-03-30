---
name: todoist-api-overdue-tasks-lenreportoverdue
description: 'Sub-skill of todoist-api: Overdue Tasks ({len(report[''overdue''])}).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Overdue Tasks ({len(report['overdue'])})

## Overdue Tasks ({len(report['overdue'])})


"""
    for task in report["overdue"]:
        content += f"- [ ] {task.content} (Due: {task.due.string})\n"

    content += f"""
