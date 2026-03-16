---
name: obsidian-tasks-due-this-week
description: 'Sub-skill of obsidian: Tasks due this week.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Tasks due this week

## Tasks due this week


```dataview
TASK
FROM "Projects"
WHERE due >= date(today) AND due <= date(today) + dur(7 days)
SORT due ASC
```
