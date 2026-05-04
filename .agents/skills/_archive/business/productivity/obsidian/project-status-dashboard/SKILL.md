---
name: obsidian-project-status-dashboard
description: 'Sub-skill of obsidian: Project Status Dashboard.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Project Status Dashboard

## Project Status Dashboard


```dataview
TABLE WITHOUT ID
  file.link as "Project",
  status as "Status",
  priority as "Priority",
  due-date as "Due Date",
  (date(due-date) - date(today)).days as "Days Left"
FROM #project
WHERE status != "completed"
SORT priority ASC, due-date ASC
```
