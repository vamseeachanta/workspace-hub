---
name: obsidian-in-progress
description: 'Sub-skill of obsidian: In Progress (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# In Progress (+1)

## In Progress


```dataview
TASK
FROM "Projects/{{title}}"
WHERE !completed AND contains(text, "WIP")
```

## Pending


```dataview
TASK
FROM "Projects/{{title}}"
WHERE !completed AND !contains(text, "WIP")
```
