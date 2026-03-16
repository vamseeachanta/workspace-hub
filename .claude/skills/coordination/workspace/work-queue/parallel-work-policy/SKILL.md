---
name: work-queue-parallel-work-policy
description: 'Sub-skill of work-queue: Parallel Work Policy.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Parallel Work Policy

## Parallel Work Policy


- Independent tasks: separate WRKs with separate evidence packages.
- Parallel related tasks: each agent modifies files only in its active WRK scope.
- Out-of-scope side effects from another agent: log, do not revert, continue.
