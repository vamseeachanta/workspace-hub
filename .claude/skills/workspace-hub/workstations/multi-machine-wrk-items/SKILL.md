---
name: workstations-multi-machine-wrk-items
description: 'Sub-skill of workstations: Multi-machine WRK Items.'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Multi-machine WRK Items

## Multi-machine WRK Items


For tasks that span machines, `computer:` accepts a list:

```yaml
computer: [licensed-win-1, dev-primary]
```

**Handoff conventions:**
- First machine listed = initiating machine
- Label each checklist step with the machine: `[dev-primary] Run mesh generation`
- `/session-start` on the second machine detects `computer:` mismatch and prompts for
  context handoff
