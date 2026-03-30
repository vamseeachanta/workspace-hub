---
name: obsidian-reading-progress
description: 'Sub-skill of obsidian: Reading Progress.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Reading Progress

## Reading Progress


```dataview
TABLE WITHOUT ID
  file.link as "Book",
  author as "Author",
  status as "Status",
  rating as "Rating"
FROM #book
WHERE status = "reading" OR status = "completed"
SORT status ASC, rating DESC
```
