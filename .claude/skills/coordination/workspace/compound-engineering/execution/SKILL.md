---
name: compound-engineering-execution
description: 'Sub-skill of compound-engineering: Execution (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Execution (+1)

## Execution


```
Delegate: core-coder (via Task)
- Convert plan into implementation
- TDD mandatory: tests first, then implementation
- Follow plan exactly; deviations require re-planning
- Commit after each logical unit of work
```


## Checkpoint


After work completes, save session state:

```yaml
# .claude/compound-state/<session-id>.yaml
session_id: <session-id>
task: "<task description>"
phase: work_complete
plan_ref: specs/modules/<module>/plan.md
commits: [<sha1>, <sha2>]
timestamp: <ISO-8601>
```
