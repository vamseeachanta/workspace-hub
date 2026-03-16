---
name: compound-engineering-checkpoint-schema
description: 'Sub-skill of compound-engineering: Checkpoint Schema.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Checkpoint Schema

## Checkpoint Schema


```yaml
session_id: string          # Unique session identifier
task: string                # Original task description
phase: string               # current phase: plan|work|review|compound|complete
plan_ref: string            # Path to plan file
review_ref: string          # Path to review report
commits: list               # Git commit SHAs produced
knowledge_entries: list     # Knowledge entry IDs created
findings_summary:           # Review findings count
  critical: int
  warning: int
  info: int
timestamp: string           # Last updated (ISO-8601)
created_at: string          # Session start (ISO-8601)
completed_at: string        # Session end (ISO-8601), null if in progress
```
