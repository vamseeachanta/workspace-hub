---
name: skills-curation-cron-schedule
description: 'Sub-skill of skills-curation: Cron Schedule.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Cron Schedule

## Cron Schedule


| Time | Job | Machine |
|------|-----|---------|
| Monday 4:00 AM | `skills-curation` (full run) | `ace-linux-1` |
| After `session-analysis.sh` | candidate intake only (Phase 1) | `ace-linux-1` |

The Monday run fires after `session-analysis.sh` (3AM) and `claude-reflect` (5AM) to have fresh candidate data available.

---
