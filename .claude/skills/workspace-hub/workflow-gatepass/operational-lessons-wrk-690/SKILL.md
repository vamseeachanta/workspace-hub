---
name: workflow-gatepass-operational-lessons-wrk-690
description: 'Sub-skill of workflow-gatepass: Operational Lessons (WRK-690).'
version: 1.0.6
category: workspace-hub
type: reference
scripts_exempt: true
---

# Operational Lessons (WRK-690)

## Operational Lessons (WRK-690)


- Explicit signal emission required (not just artifact presence); shared scripts must log lifecycle signals.
- User-review stages emit both stage signal AND browser-open signal (not collapsed).
- Keep close/archive signals distinct; emit `close_or_archive` aggregation for weekly reporting.
- Multi-agent: out-of-scope side effects are non-blocking; document under `Out-of-Scope Side Effects`.
