---
name: obsidian-meetings
description: 'Sub-skill of obsidian: Meetings.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Meetings

## Meetings


```dataview
TABLE WITHOUT ID
  file.link as "Meeting",
  attendees as "Attendees"
FROM #meeting
WHERE date = date("{{date:YYYY-MM-DD}}")
```
