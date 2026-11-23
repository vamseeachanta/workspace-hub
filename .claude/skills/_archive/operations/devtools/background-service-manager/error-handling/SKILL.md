---
name: background-service-manager-error-handling
description: 'Sub-skill of background-service-manager: Error Handling.'
version: 2.0.0
category: operations
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Errors


**Error: "Already running"**
- Cause: Stale PID file from crashed process
- Solution: Check if process actually running, remove stale PID file

**Error: "Permission denied"**
- Cause: Script not executable or wrong user
- Solution: `chmod +x service.sh`, check file ownership

**Error: Process dies immediately**
- Cause: Command fails on startup

*See sub-skills for full details.*
