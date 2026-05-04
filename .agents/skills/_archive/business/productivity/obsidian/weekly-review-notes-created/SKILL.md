---
name: obsidian-weekly-review-notes-created
description: 'Sub-skill of obsidian: Weekly Review - Notes Created.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Weekly Review - Notes Created

## Weekly Review - Notes Created


```dataview
TABLE WITHOUT ID
  file.link as "Note",
  file.ctime as "Created"
FROM ""
WHERE file.ctime >= date(today) - dur(7 days)
  AND !contains(file.path, "Templates")
SORT file.ctime DESC
```
