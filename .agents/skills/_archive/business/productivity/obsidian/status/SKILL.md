---
name: obsidian-status
description: 'Sub-skill of obsidian: Status.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Status

## Status


```dataview
TABLE WITHOUT ID
  status as "Status",
  due-date as "Due Date",
  priority as "Priority"
WHERE file.name = this.file.name
```
