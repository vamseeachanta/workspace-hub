---
name: agent-teams-core-constraint
description: 'Sub-skill of agent-teams: Core Constraint.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Core Constraint

## Core Constraint


```
MAX_TEAMMATES = 10  (set in .claude/settings.json — git-tracked)
Recommended sweet spot: 2–3 teammates for this workspace's workload
```

Default to **fewer agents**, not more. Spawn only as many as strictly needed.
Coordination overhead grows quadratically; benefits only appear when tasks are
truly parallel and long-running.

`MAX_TEAMMATES=10` is a ceiling, not a target. The realistic effective range
for workspace-hub engineering work is **2–3 teammates**. Raising it above that
adds token cost with diminishing returns given the predominantly sequential
solver-pipeline nature of the work.
