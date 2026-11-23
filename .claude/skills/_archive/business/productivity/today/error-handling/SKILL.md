---
name: today-error-handling
description: 'Sub-skill of today: Error Handling.'
version: 1.1.0
category: business
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


| Situation | Action |
|-----------|--------|
| No git activity | Note "No commits" - suggest catching up |
| Missing config | Use defaults, create template config |
| Calendar unavailable | Skip calendar section, note in summary |
| Cron fails | Check log at `/tmp/daily_today.log` |
