---
name: obsidian-meeting-action-items
description: 'Sub-skill of obsidian: Meeting Action Items.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Meeting Action Items

## Meeting Action Items


```dataview
TASK
FROM #meeting
WHERE !completed AND contains(text, "@")
GROUP BY file.link
SORT file.ctime DESC
```
