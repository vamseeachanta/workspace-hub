---
name: todoist-api-waiting-for-lenreportwaitingfor
description: 'Sub-skill of todoist-api: Waiting For ({len(report[''waiting_for''])}).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Waiting For ({len(report['waiting_for'])})

## Waiting For ({len(report['waiting_for'])})


"""
    for task in report["waiting_for"]:
        content += f"- {task.content}\n"

    content += f"""
