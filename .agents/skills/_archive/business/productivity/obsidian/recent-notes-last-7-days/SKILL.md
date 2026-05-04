---
name: obsidian-recent-notes-last-7-days
description: 'Sub-skill of obsidian: Recent notes (last 7 days).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Recent notes (last 7 days)

## Recent notes (last 7 days)


```dataview
TABLE file.ctime as "Created", file.mtime as "Modified"
FROM ""
WHERE file.ctime >= date(today) - dur(7 days)
SORT file.ctime DESC
LIMIT 10
```
```

**Advanced Dataview Queries:**
```markdown
