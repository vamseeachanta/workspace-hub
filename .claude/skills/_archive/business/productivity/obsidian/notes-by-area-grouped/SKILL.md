---
name: obsidian-notes-by-area-grouped
description: 'Sub-skill of obsidian: Notes by Area (grouped).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Notes by Area (grouped)

## Notes by Area (grouped)


```dataview
TABLE WITHOUT ID
  file.link as "Note",
  file.mtime as "Last Modified"
FROM "Areas"
GROUP BY file.folder
SORT file.mtime DESC
```
